"use client"

import React, { useState, useMemo } from 'react'
import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Loader2, X, Plus, Search, BarChart3, Globe, MapPin, TrendingUp } from "lucide-react"
import { getStageName } from '@/lib/utils'
import AnalysisLoading from '@/components/ui/analysis-loading'
import { Pie, PieChart, Sector, Cell } from "recharts"
import { PieSectorDataItem } from "recharts/types/polar/Pie"
import {
    ChartConfig,
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart"
import { Helix } from 'ldrs/react'
import 'ldrs/react/Helix.css'


interface Company {
    company: string
    relevantUrls: string[]
    times_cited: number
}

interface AnalysisState {
    step: 'input' | 'keywords' | 'results'
    loading: boolean
    sessionId: string | null
    currentAnalysysStage: null | string
    formData: {
        brand_name: string
        city: string
        language: 'pt_BR' | 'en_US'
    }
    keywords: string[]
    editedKeywords: string[]
    newKeyword: string
    results: Company[]
    error: string | null
}

const maxKeywords = 10
const sortAndGroupCompanies = (companies: Company[]) => {
    const sortedCompanies = [...companies].sort((a, b) => b.times_cited - a.times_cited)

    const normalizeCompanyName = (name: string): string => {
        return name
            .toLowerCase()
            .replace(/\b(ltda|ltd|inc|corp|corporation|llc|sa|s\.a\.|distribuidora|comercial|cia|company)\b/g, '')
            .replace(/[^\w\s]/g, '') // Punctiatio
            .replace(/\s+/g, ' ')
            .trim()
    }

    const areNamesSimilar = (name1: string, name2: string): boolean => {
        const normalized1 = normalizeCompanyName(name1)
        const normalized2 = normalizeCompanyName(name2)

        return normalized1.includes(normalized2) || normalized2.includes(normalized1)
    }

    const groupedCompanies: { [key: string]: Company } = {}

    sortedCompanies.forEach(company => {
        const existingKey = Object.keys(groupedCompanies).find(key =>
            areNamesSimilar(key, company.company)
        )

        if (existingKey) {
            groupedCompanies[existingKey].times_cited += company.times_cited
            groupedCompanies[existingKey].relevantUrls.push(...company.relevantUrls)
        } else {
            groupedCompanies[company.company] = {
                ...company,
                relevantUrls: [...company.relevantUrls]
            }
        }
    })

    return Object.values(groupedCompanies)
        .map(company => ({
            ...company,
            relevantUrls: Array.from(new Set(company.relevantUrls))
        }))
        .sort((a, b) => b.times_cited - a.times_cited) // sort again after group
}


const GeoEvaluator = () => {
    const [state, setState] = useState<AnalysisState>({
        step: 'input',
        loading: false,
        sessionId: null,
        currentAnalysysStage: null,
        formData: {
            brand_name: '',
            city: '',
            language: 'en_US'
        },
        keywords: [],
        editedKeywords: [],
        newKeyword: '',
        results: [],
        error: null
    })

    const startAnalysis = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!state.formData.brand_name.trim()) {
            setState(prev => ({ ...prev, error: 'Company name is required' }))
            return
        }

        setState(prev => ({ ...prev, loading: true, error: null }))

        try {
            const response = await fetch('http://localhost:8000/stream/analyze/get_keywords', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(state.formData),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }
            if (!response.body) {
                throw new Error('Response body is null')
            }

            setState(prev => ({ ...prev, currentAnalysysStage: 'starting', step: 'keywords' }))

            const reader = response.body.getReader()
            const decoder = new TextDecoder()

            try {
                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunk = decoder.decode(value, { stream: true })
                    const lines = chunk.split('\n').filter(line => line.trim())
                    for (const line of lines) {
                        const data = JSON.parse(line)


                        switch (data.stage) {
                            case 'initializing':
                                setState(prev => ({
                                    ...prev,
                                    currentAnalysysStage: "Setting up the language model and preparing the analysis environment...",
                                    sessionId: data.session_id
                                }))
                                break

                            case 'analysys':
                                const operationName = Object.keys(data.data)[0]
                                const template = getStageName(operationName)
                                setState(prev => ({
                                    ...prev,
                                    currentAnalysysStage: template,
                                }))
                                break

                            case 'completed':
                                setState(prev => ({
                                    ...prev,
                                    loading: false,
                                    step: 'keywords',
                                    currentAnalysysStage: null,
                                    sessionId: data.session_id,
                                    keywords: data.data.keywords || [],
                                    editedKeywords: data.data.keywords || []
                                }))
                                console.log('✅ Analysis completed!')
                                break

                            case 'error':
                                throw new Error(data.data)
                        }
                    }

                }
            } catch (error: any) {
                setState(prev => ({
                    ...prev,
                    loading: false,
                    error: `Failed to read response: ${error.message}`
                }))
                return
            }
        } catch (error) {
            setState(prev => ({
                ...prev,
                loading: false,
                error: `Failed to start analysis: ${error instanceof Error ? error.message : 'Unknown error'}`
            }))
        }
    }

    const getRankings = async () => {
        if (!state.sessionId) return

        setState(prev => ({ ...prev, loading: true, error: null }))

        try {
            const response = await fetch('http://localhost:8000/stream/analyze/get_rankings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: state.sessionId,
                    keywords: state.editedKeywords
                }),
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
            }
            if (!response.body) {
                throw new Error('Response body is null')
            }

            setState(prev => ({ ...prev, step: 'results' }))

            const reader = response.body.getReader()
            const decoder = new TextDecoder()

            try {
                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunk = decoder.decode(value, { stream: true })
                    const lines = chunk.split('\n').filter(line => line.trim())
                    for (const line of lines) {
                        const data = JSON.parse(line)
                        console.log(data)

                        switch (data.stage) {
                            case 'initializing':
                                break;
                            case 'gathering_results':
                                const progressGraphData = data.data.gather_results.graph || []
                                const graphPieChartDataProgress = progressGraphData.map((company: any) => ({
                                    company: company.__dict__.name,
                                    times_cited: company.__dict__.times_cited,
                                    relevantUrls: company.__dict__.relevantUrls
                                }))

                                setState(prev => ({
                                    ...prev,
                                    results: graphPieChartDataProgress
                                }))
                                break

                            case 'completed':
                                const rawGraphData = data.data.graph || []

                                const graphPieChartData = rawGraphData.map((company: any) => ({
                                    company: company.__dict__.name,
                                    times_cited: company.__dict__.times_cited,
                                    relevantUrls: company.__dict__.relevantUrls
                                }))

                                const sortedResults = sortAndGroupCompanies(graphPieChartData)


                                setState(prev => ({
                                    ...prev,
                                    loading: false,
                                    results: sortedResults,
                                    currentAnalysysStage: null
                                }))
                                break
                            case 'error':
                                throw new Error(data.data)
                        }
                    }

                }
            } catch (error: any) {
                setState(prev => ({
                    ...prev,
                    loading: false,
                    error: `Failed to read response: ${error.message}`
                }))
                return
            }
        } catch (error) {
            setState(prev => ({
                ...prev,
                loading: false,
                error: `Failed to refine analysis: ${error instanceof Error ? error.message : 'Unknown error'}`
            }))
        }
    }

    const removeKeyword = (index: number) => {
        setState(prev => ({
            ...prev,
            editedKeywords: prev.editedKeywords.filter((_, i) => i !== index)
        }))
    }

    const addKeyword = () => {
        if (state.newKeyword.trim() && state.editedKeywords.length < maxKeywords) {
            setState(prev => ({
                ...prev,
                editedKeywords: [...prev.editedKeywords, prev.newKeyword.trim()],
                newKeyword: ''
            }))
        }
    }

    const resetAnalysis = () => {
        setState({
            step: 'input',
            loading: false,
            sessionId: null,
            currentAnalysysStage: null,
            formData: {
                brand_name: '',
                city: '',
                language: 'en_US'
            },
            keywords: [],
            editedKeywords: [],
            newKeyword: '',
            results: [],
            error: null
        })
    }

    // Create chart data and configuration
    const chartData = useMemo(() => {
        const data =  state.results.map((company, index) => ({
            company: company.company,
            times_cited: company.times_cited,
            fill: `var(--chart-${(index % 5) + 1})`,
        }))
        console.log(data)
        return data
    }, [state.results])

    const chartConfig = useMemo(() => {
        const config: ChartConfig = {
            times_cited: {
                label: "Times Cited",
            },
        }

        state.results.forEach((company, index) => {
            config[company.company.toLowerCase().replace(/\s+/g, '_')] = {
                label: company.company,
                color: `var(--chart-${(index % 5) + 1})`,
            }
        })

        return config
    }, [state.results])


    return (
        <div className='min-h-screen bg-background'>
            <div className='container mx-auto py-8'>
                <div className='text-center mb-8'>
                    <h1 className='text-4xl font-bold tracking-tight'>
                        🌍 GEO Evaluator
                    </h1>
                    <p className='text-xl text-muted-foreground mt-2'>
                        Generative Engine Optimization Analysis
                    </p>
                </div>

                {state.error && (
                    <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
                        {state.error}
                    </div>
                )}

                <div className='w-full mt-12 p-8'>
                    <div className='flex flex-col gap-8' style={{ minHeight: 'calc(100vh - 280px)' }}>
                        <div className='w-full flex gap-8' >
                            <Card className="w-full lg:w-1/2 flex flex-col" style={{ minHeight: 'calc(100vh - 280px)' }}>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <MapPin className="h-5 w-5" />
                                        Company Details
                                    </CardTitle>
                                    <CardDescription>
                                        Enter your company details and targeted market for analysis
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="flex-1">
                                    <form onSubmit={startAnalysis}>
                                        <div className="flex flex-col gap-4">
                                            <div className="grid gap-2">
                                                <Label htmlFor="brand_name">Company name</Label>
                                                <Input
                                                    id="brand_name"
                                                    type="text"
                                                    placeholder="Acme Inc."
                                                    value={state.formData.brand_name}
                                                    onChange={(e) => setState(prev => ({
                                                        ...prev,
                                                        formData: { ...prev.formData, brand_name: e.target.value }
                                                    }))}
                                                    required
                                                />
                                            </div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="city">City (optional)</Label>
                                                <Input
                                                    id="city"
                                                    type="text"
                                                    placeholder='Paris'
                                                    value={state.formData.city}
                                                    onChange={(e) => setState(prev => ({
                                                        ...prev,
                                                        formData: { ...prev.formData, city: e.target.value }
                                                    }))}
                                                />
                                            </div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="language">Language/Market</Label>
                                                <select
                                                    id="language"
                                                    value={state.formData.language}
                                                    onChange={(e) => setState(prev => ({
                                                        ...prev,
                                                        formData: { ...prev.formData, language: e.target.value as 'pt_BR' | 'en_US' }
                                                    }))}
                                                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                                                >
                                                    <option value="en_US">🇺🇸 English (US)</option>
                                                    <option value="pt_BR">🇧🇷 Portuguese (BR)</option>
                                                </select>
                                            </div>
                                        </div>
                                    </form>
                                </CardContent>
                                <CardFooter className="mt-auto">
                                    {state.step === 'input' && !state.loading ? (
                                        <Button
                                            onClick={startAnalysis}
                                            className="w-full"
                                            disabled={state.loading}
                                        >
                                            <>
                                                <Search className="mr-2 h-4 w-4" />
                                                Start Analysis
                                            </>
                                        </Button>
                                    ) : (
                                        <div className="flex gap-2 w-full">
                                            <Button
                                                onClick={startAnalysis}
                                                variant="outline"
                                                className="flex-1"
                                                disabled={state.loading}
                                            >
                                                <Search className="mr-2 h-4 w-4" />
                                                Re-analyze
                                            </Button>
                                            <Button
                                                onClick={resetAnalysis}
                                                variant="outline"
                                                className="flex-1"
                                            >
                                                Reset
                                            </Button>
                                        </div>
                                    )}
                                </CardFooter>
                            </Card>

                            <Card className={`w-full lg:w-1/2 flex flex-col ${state.step === 'input' && state.keywords.length === 0 ? 'opacity-50' : ''}`} style={{ minHeight: 'calc(100vh - 280px)' }}>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Globe className="h-5 w-5" />
                                        Analysis
                                    </CardTitle>
                                    <CardDescription>
                                        {state.keywords.length === 0
                                            ? 'Keywords will appear here after analysis starts'
                                            : `Edit, add or remove keywords for your analysis (max ${maxKeywords})`
                                        }
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="flex-1">
                                    <div className="space-y-4">
                                        {state.keywords.length === 0 ? (
                                            <div className="space-y-4">
                                                <AnalysisLoading
                                                    currentStage={state.currentAnalysysStage}
                                                    isLoading={state.loading}
                                                />

                                                {!state.loading && !state.currentAnalysysStage && (
                                                    <>
                                                        <div className="flex flex-wrap gap-2">
                                                            <Badge variant="outline" className="opacity-30">Keyword 1</Badge>
                                                            <Badge variant="outline" className="opacity-30">Keyword 2</Badge>
                                                            <Badge variant="outline" className="opacity-30">Keyword 3</Badge>
                                                        </div>

                                                        <div className="flex gap-2">
                                                            <Input
                                                                placeholder="Add new keyword..."
                                                                disabled
                                                                className="opacity-50"
                                                            />
                                                            <Button size="icon" disabled className="opacity-50">
                                                                <Plus className="h-4 w-4" />
                                                            </Button>
                                                        </div>

                                                        <p className="text-sm text-muted-foreground opacity-50">
                                                            0/{maxKeywords} keywords
                                                        </p>
                                                    </>
                                                )}
                                            </div>
                                        ) : (
                                            <div className="space-y-4">
                                                <div className="flex flex-wrap gap-2">
                                                    {state.editedKeywords.map((keyword, index) => (
                                                        <Badge
                                                            key={index}
                                                            variant="secondary"
                                                            className="flex items-center gap-1"
                                                        >
                                                            {keyword}
                                                            <X
                                                                className="h-3 w-3 cursor-pointer hover:text-destructive"
                                                                onClick={() => removeKeyword(index)}
                                                            />
                                                        </Badge>
                                                    ))}
                                                </div>

                                                {state.editedKeywords.length < maxKeywords && (
                                                    <div className="flex gap-2">
                                                        <Input
                                                            placeholder="Add new keyword..."
                                                            value={state.newKeyword}
                                                            onChange={(e) => setState(prev => ({ ...prev, newKeyword: e.target.value }))}
                                                            onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
                                                        />
                                                        <Button
                                                            onClick={addKeyword}
                                                            size="icon"
                                                            disabled={!state.newKeyword.trim()}
                                                        >
                                                            <Plus className="h-4 w-4" />
                                                        </Button>
                                                    </div>
                                                )}

                                                <p className="text-sm text-muted-foreground">
                                                    {state.editedKeywords.length}/{maxKeywords} keywords
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                                <CardFooter className="mt-auto">
                                    <Button
                                        onClick={getRankings}
                                        className="w-full"
                                        disabled={state.loading || state.editedKeywords.length === 0}
                                    >
                                        {state.loading ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Processing...
                                            </>
                                        ) : (
                                            <>
                                                <BarChart3 className="mr-2 h-4 w-4" />
                                                {state.step === 'results' ? 'Update Results' : 'Generate Results'}
                                            </>
                                        )}
                                    </Button>
                                </CardFooter>
                            </Card>

                        </div>

                        {state.step === 'results' && (
                            <div className="w-full flex flex-wrap gap-8">
                                {/* Companies List */}
                                <Card className="w-full lg:w-1/2 flex flex-col">
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <BarChart3 className="h-5 w-5" />
                                            Analysis Results
                                        </CardTitle>
                                        <CardDescription>
                                            Companies found in GEO analysis for your keywords
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent className="flex-1 overflow-auto">
                                        <div className="space-y-4">
                                            {state.results.length === 0 ? (
                                                <p className="text-muted-foreground text-center py-4">
                                                    <Helix
                                                    size="80"
                                                    speed="2.5"
                                                    color="black" 
                                                    />
                                                </p>
                                            ) : (
                                                state.results.map((company, index) => (
                                                    <div key={index} className="border rounded-lg p-4 space-y-2">
                                                        <div className="flex justify-between items-start">
                                                            <h3 className="font-semibold">{company.company}</h3>
                                                            <Badge variant="outline">
                                                                {company.times_cited} mentions
                                                            </Badge>
                                                        </div>
                                                        {company.relevantUrls.length > 0 && (
                                                            <div className="space-y-1">
                                                                <p className="text-sm text-muted-foreground">Relevant URLs:</p>
                                                                {company.relevantUrls.slice(0, 3).map((url, urlIndex) => (
                                                                    <a
                                                                        key={urlIndex}
                                                                        href={url}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="text-xs text-blue-600 hover:underline block truncate"
                                                                    >
                                                                        {url}
                                                                    </a>
                                                                ))}
                                                                {company.relevantUrls.length > 3 && (
                                                                    <p className="text-xs text-muted-foreground">
                                                                        +{company.relevantUrls.length - 3} more URLs
                                                                    </p>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    </CardContent>
                                </Card>

                                {state.results.length > 0 && (
                                    <Card className="w-full lg:w-1/2 h-[500px] flex flex-col">
                                        <CardHeader className="items-center pb-0">
                                            <CardTitle>Company Mentions Distribution</CardTitle>
                                            <CardDescription>
                                                Analysis results for {state.formData.brand_name}
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent className="flex-1 pb-0 flex items-center justify-center">
                                            <ChartContainer
                                                config={chartConfig}
                                                className="mx-auto aspect-square max-h-[300px]"
                                            >
                                                <PieChart>
                                                    <ChartTooltip
                                                        cursor={false}
                                                        content={<ChartTooltipContent hideLabel />}
                                                    />
                                                    <Pie
                                                        data={chartData}
                                                        dataKey="times_cited"
                                                        nameKey="company"
                                                        innerRadius={60}
                                                        strokeWidth={5}
                                                        activeShape={({
                                                            outerRadius = 0,
                                                            ...props
                                                        }: PieSectorDataItem) => (
                                                            <Sector {...props} outerRadius={outerRadius + 10} />
                                                        )}
                                                    />
                                                </PieChart>
                                            </ChartContainer>
                                        </CardContent>
                                        <CardFooter className="flex-col gap-2 text-sm">
                                            <div className="flex items-center gap-2 leading-none font-medium">
                                                Total companies analyzed: {state.results.length} <TrendingUp className="h-4 w-4" />
                                            </div>
                                            <div className="text-muted-foreground leading-none">
                                                Showing citation frequency across all analyzed companies
                                            </div>
                                        </CardFooter>
                                    </Card>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default GeoEvaluator