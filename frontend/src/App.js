import React, { useState } from 'react';
import './App.css';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from './components/ui/alert';
import { Loader2, Shield, AlertTriangle, CheckCircle, ExternalLink, Download } from 'lucide-react';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    setLoading(true);
    setError('');
    setAnalysis(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score) => {
    if (score <= 30) return 'text-green-600 bg-green-50';
    if (score <= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getRiskLevel = (score) => {
    if (score <= 30) return 'Low Risk';
    if (score <= 60) return 'Medium Risk';
    return 'High Risk';
  };

  const getSeverityColor = (severity) => {
    if (severity <= 3) return 'bg-green-100 text-green-800';
    if (severity <= 6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const exportReport = () => {
    if (!analysis) return;
    
    const reportContent = `Terms & Conditions Risk Analysis Report
========================================

URL: ${analysis.url}
Document: ${analysis.title}
Risk Score: ${analysis.risk_score}/100 (${getRiskLevel(analysis.risk_score)})
Analysis Time: ${analysis.analysis_time.toFixed(2)} seconds

SUMMARY:
${analysis.summary.map((point, index) => `${index + 1}. ${point}`).join('\n')}

IDENTIFIED RISKS:
${analysis.risks.map((risk, index) => `
${index + 1}. ${risk.title}
   Category: ${risk.category}
   Severity: ${risk.severity}/10
   Description: ${risk.description}
   ${risk.excerpt ? `Relevant Text: "${risk.excerpt}"` : ''}
`).join('\n')}

Generated on: ${new Date().toLocaleString()}
`;

    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `risk-analysis-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <Shield className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Terms & Conditions Risk Analyzer</h1>
              <p className="text-sm text-slate-600">Understand the risks before you agree</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {/* Input Section */}
        <Card className="bg-white/90 backdrop-blur-sm border-slate-200 shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl text-slate-900">Analyze Terms & Conditions</CardTitle>
            <CardDescription className="text-slate-600">
              Enter the URL of any Terms of Service, Privacy Policy, or EULA to get an instant risk analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  type="url"
                  placeholder="https://example.com/terms-and-conditions"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1 border-slate-300 focus:border-blue-500"
                  disabled={loading}
                />
                <Button 
                  onClick={handleAnalyze} 
                  disabled={loading || !url.trim()}
                  className="px-6 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    'Analyze'
                  )}
                </Button>
              </div>
              
              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle className="text-red-800">Error</AlertTitle>
                  <AlertDescription className="text-red-700">{error}</AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        {analysis && (
          <div className="space-y-6">
            {/* Risk Score Overview */}
            <Card className="bg-white/90 backdrop-blur-sm border-slate-200 shadow-lg">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl text-slate-900 flex items-center space-x-2">
                      <ExternalLink className="h-5 w-5" />
                      <span>{analysis.title}</span>
                    </CardTitle>
                    <CardDescription className="text-slate-600 mt-1">
                      <a href={analysis.url} target="_blank" rel="noopener noreferrer" 
                         className="text-blue-600 hover:text-blue-800 underline">
                        {analysis.url}
                      </a>
                    </CardDescription>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={exportReport}
                    className="flex items-center space-x-1"
                  >
                    <Download className="h-4 w-4" />
                    <span>Export Report</span>
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-6">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-slate-700">Risk Score</span>
                      <span className={`text-lg font-bold px-3 py-1 rounded-full ${getRiskColor(analysis.risk_score)}`}>
                        {analysis.risk_score}/100
                      </span>
                    </div>
                    <Progress value={analysis.risk_score} className="h-3" />
                    <div className="flex justify-between mt-2 text-xs text-slate-600">
                      <span>Low Risk (0-30)</span>
                      <span>Medium Risk (31-60)</span>
                      <span>High Risk (61-100)</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge 
                      variant="secondary" 
                      className={`text-base px-4 py-2 ${getRiskColor(analysis.risk_score)}`}
                    >
                      {getRiskLevel(analysis.risk_score)}
                    </Badge>
                    <p className="text-xs text-slate-600 mt-1">
                      Analysis completed in {analysis.analysis_time.toFixed(2)}s
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Summary */}
            <Card className="bg-white/90 backdrop-blur-sm border-slate-200 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg text-slate-900 flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>Key Points Summary</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {analysis.summary.map((point, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-slate-700">{point}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Risks */}
            <Card className="bg-white/90 backdrop-blur-sm border-slate-200 shadow-lg">
              <CardHeader>
                <CardTitle className="text-lg text-slate-900 flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-orange-600" />
                  <span>Identified Risks</span>
                </CardTitle>
                <CardDescription>
                  {analysis.risks.length} potential risk{analysis.risks.length !== 1 ? 's' : ''} found
                </CardDescription>
              </CardHeader>
              <CardContent>
                {analysis.risks.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
                    <p className="text-slate-600">No significant risks identified in this document.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {analysis.risks.map((risk, index) => (
                      <div key={index} className="border border-slate-200 rounded-lg p-4 bg-slate-50/50">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold text-slate-900">{risk.title}</h4>
                          <Badge className={`${getSeverityColor(risk.severity)} text-xs`}>
                            Severity: {risk.severity}/10
                          </Badge>
                        </div>
                        <p className="text-slate-700 mb-3">{risk.description}</p>
                        {risk.excerpt && (
                          <div className="bg-white border border-slate-200 rounded p-3">
                            <p className="text-xs font-medium text-slate-600 mb-1">Relevant Text:</p>
                            <p className="text-sm text-slate-800 italic">"{risk.excerpt}"</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-sm border-t border-slate-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center">
          <p className="text-slate-600 text-sm">
            Terms & Conditions Risk Analyzer - Helping you understand legal agreements before you sign
          </p>
          <p className="text-slate-500 text-xs mt-1">
            Powered by AI • Always consult a legal professional for important decisions
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;