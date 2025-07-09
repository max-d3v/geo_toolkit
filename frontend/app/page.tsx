import Image from "next/image";
import { Navbar } from "@/components/ui/navbar";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
      <Navbar />
      <div className="max-w-4xl mx-auto mt-[20vh]">
        <h1 className="text-5xl md:text-6xl font-display text-slate-900 mb-4">
          GEO Agents
        </h1>
        <h2 className="text-2xl md:text-3xl font-display text-slate-700 mb-8">
          Next Generation Marketing
        </h2>
        <div className="prose prose-lg max-w-none">
          <p className="text-lg text-slate-600 leading-relaxed mb-6">
            Welcome to the future of geographical marketing intelligence. Our advanced agents
            leverage cutting-edge technology to deliver unprecedented insights.
          </p>
          <div className="grid md:grid-cols-2 gap-8 mt-12">
            <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-white/20">
              <h3 className="text-xl font-display text-slate-800 mb-3">Intelligence</h3>
              <p className="text-slate-600">
                Advanced algorithms analyze geographical patterns and market trends.
              </p>
            </div>
            <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-sm border border-white/20">
              <h3 className="text-xl font-display text-slate-800 mb-3">Precision</h3>
              <p className="text-slate-600">
                Targeted insights with pixel-perfect accuracy for your campaigns.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>  );
}
