"use client"

import * as React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { Menu, X, ChevronDown, Wrench } from "lucide-react"

interface NavbarProps {
  className?: string
}

export function Navbar({ className }: NavbarProps) {
  const [isOpen, setIsOpen] = React.useState(false)

  return (
    <header 
      className={cn(
        "fixed top-6 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-4xl mx-auto",
        className
      )}
    >
      <div className="mx-4">
        <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border border-gray-200/20 dark:border-gray-700/20 rounded-2xl shadow-lg shadow-black/5 px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-2">
              <span className="font-bold text-xl font-playfair text-gray-900 dark:text-white">
                GEO agents
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link
                href="/"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200 font-medium"
              >
                Home
              </Link>
              
              {/* Tools Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200 font-medium px-0"
                  >
                    Ferramentas
                    <ChevronDown className="ml-1 h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent 
                  align="center" 
                  className="w-56 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-gray-200/20 dark:border-gray-700/20"
                >
                  <DropdownMenuLabel className="text-gray-900 dark:text-white">
                    Ferramentas
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link 
                      href="/geo_aval" 
                      className="flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
                    >
                      <Wrench className="h-4 w-4" />
                      GEO Aval
                      <span className="ml-auto text-xs text-gray-400">v1.0</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem disabled className="text-gray-400 dark:text-gray-500">
                    <span className="text-xs">Mais ferramentas em breve...</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Link
                href="/about"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200 font-medium"
              >
                Sobre
              </Link>
              <Link
                href="/contact"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200 font-medium"
              >
                Contato
              </Link>
            </div>

            {/* Right side - Desktop */}
            <div className="hidden md:flex items-center space-x-3">
              <Button variant="ghost" size="sm" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                Login
              </Button>
              <Button size="sm" variant="outline">
                Começar
              </Button>
            </div>

            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              <span className="sr-only">Toggle menu</span>
            </Button>
          </div>

          {/* Mobile Navigation Menu */}
          {isOpen && (
            <div className="md:hidden mt-4 pt-4 border-t border-gray-200/20 dark:border-gray-700/20">
              <nav className="flex flex-col space-y-3">
                <Link
                  href="/"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200 font-medium py-2"
                  onClick={() => setIsOpen(false)}
                >
                  Home
                </Link>
                
                {/* Mobile Tools Section */}
                <div className="py-2">
                  <span className="text-gray-500 dark:text-gray-400 text-sm font-medium mb-2 block">
                    Ferramentas
                  </span>
                  <Link
                    href="/geo_aval"
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200 font-medium py-1 pl-4"
                    onClick={() => setIsOpen(false)}
                  >
                    <Wrench className="h-4 w-4" />
                    GEO Aval
                  </Link>
                </div>

                <Link
                  href="/about"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200 font-medium py-2"
                  onClick={() => setIsOpen(false)}
                >
                  Sobre
                </Link>
                <Link
                  href="/contact"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors duration-200 font-medium py-2"
                  onClick={() => setIsOpen(false)}
                >
                  Contato
                </Link>
                
                <div className="flex flex-col space-y-2 pt-3 border-t border-gray-200/20 dark:border-gray-700/20">
                  <Button variant="ghost" className="justify-start text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                    Login
                  </Button>
                  <Button variant="outline">
                    Começar
                  </Button>
                </div>
              </nav>
            </div>
          )}
        </nav>
      </div>
    </header>
  )
}