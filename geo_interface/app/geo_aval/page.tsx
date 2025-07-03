import React from 'react'
import KeywordCard from '@/components/ui/keywords_card'
import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
    CardAction
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

const Page = () => {
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

            </div>

            <div className='w-full mt-12 p-8 flex-col' >
                <div className='flex' >
                    { /* Card 1 for  basic data: language, city company name. */}
                    <Card className="w-full max-w-sm h-[40vh]">
                        <CardHeader  > 
                            <CardTitle>Input info</CardTitle>
                            <CardDescription>
                                Enter your company details and targeted market / location for analysis
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <form>
                                <div className="flex flex-col gap-6">
                                    <div className="grid gap-2">
                                        <Label htmlFor="name">Company name</Label>
                                        <Input
                                            id="name"
                                            type="text"
                                            placeholder="Acme Inc."
                                            required
                                        />
                                    </div>
                                    <div className="grid gap-2">
                                        <div className="flex items-center">
                                            <Label htmlFor="location">Location (city)</Label>
                                        </div>
                                        <Input id="location" type="text" placeholder='Paris' required />
                                    </div>
                                </div>
                            </form>
                        </CardContent>
                        <CardFooter className="flex-col gap-2">
                            <Button type="submit" className="w-full">
                                Continue
                            </Button>
                        </CardFooter>
                    </Card>

                    { /* Interactive keyword card with keywords returned and keyword edits for resending to api  */}
                </div>
                { /* full width card with graph and all the data */}
            </div>
        </div>
    )
}

export default Page