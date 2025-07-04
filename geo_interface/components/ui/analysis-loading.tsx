import { Loader2, CheckCircle, Clock } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface AnalysisLoadingProps {
    currentStage: string | null
    isLoading: boolean
}

const AnalysisLoading = ({ currentStage, isLoading }: AnalysisLoadingProps) => {
    if (!isLoading && !currentStage) return null

    return (
        <Card className="w-full border-primary/20 bg-primary/5">
            <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-sm">
                    {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin text-primary" />
                    ) : (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                    )}
                    Analysis in Progress
                </CardTitle>
                <CardDescription className="text-xs">
                    {isLoading ? "Processing your request..." : "Analysis completed"}
                </CardDescription>
            </CardHeader>
            <CardContent className="pt-0">
                <div className="space-y-3">
                    {/* Current Stage Display */}
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Current Stage:</span>
                        <Badge variant={isLoading ? "default" : "secondary"} className="text-xs">
                            {getStageDisplayName(currentStage) || "Waiting..."}
                        </Badge>
                    </div>

                    {/* Progress Animation */}
                    {isLoading && (
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs text-muted-foreground">
                                <span>Processing</span>
                                <Clock className="h-3 w-3" />
                            </div>
                            <div className="w-full bg-secondary rounded-full h-1.5">
                                <div className="bg-primary h-1.5 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                            </div>
                        </div>
                    )}

                    {/* Stage Description */}
                    <p className="text-xs text-muted-foreground leading-relaxed">
                        {getStageDescription(currentStage)}
                    </p>
                </div>
            </CardContent>
        </Card>
    )
}

const getStageDisplayName = (stage: string | null): string => {
    if (!stage) return "Waiting"
    
    // Extract operation name if it's a template string
    if (stage.includes("Extracting") || stage.includes("keywords")) return "Keywords Extraction"
    if (stage.includes("Searching") || stage.includes("search")) return "Information Search"
    if (stage.includes("Analyzing") || stage.includes("analysis")) return "Data Analysis"
    if (stage.includes("Setting up") || stage.includes("language model")) return "Initializing"
    if (stage.includes("Generating") || stage.includes("results")) return "Results Generation"
    
    return "Processing"
}

const getStageDescription = (stage: string | null): string => {
    if (!stage) return "Please wait while we process your analysis request."
    
    if (stage.includes("Setting up") || stage.includes("language model")) {
        return "Setting up the language model and preparing the analysis environment..."
    }
    if (stage.includes("Extracting") || stage.includes("keywords")) {
        return "Extracting relevant keywords from your company information..."
    }
    if (stage.includes("Searching") || stage.includes("search")) {
        return "Searching for information across multiple sources..."
    }
    if (stage.includes("Analyzing") || stage.includes("analysis")) {
        return "Processing and analyzing the collected data..."
    }
    if (stage.includes("Generating") || stage.includes("results")) {
        return "Compiling the final analysis results..."
    }
    
    return stage || "Processing your request..."
}

export default AnalysisLoading