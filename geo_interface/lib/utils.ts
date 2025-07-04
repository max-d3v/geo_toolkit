import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getStageName(stageName: string): string {
  switch (stageName) {
    case "web_research":
      return "Researching web for company data"
    case "get_keywords":
      return "Extracting relevant keywords from your company information..."
    case "refine_keywords":
      return "Refining chosen keywords"
    default:
      return stageName
  }
}