import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertCircle, RotateCcw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error caught by ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  public handleGoHome = () => {
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[400px] h-full flex items-center justify-center p-6 bg-[#F7F8FA] font-sans">
          <div className="max-w-lg w-full bg-white p-8 rounded-portal border border-[#CBD5E1] shadow-portal-elevated space-y-5">
            <div className="flex items-center gap-3 border-b border-[#E8ECF2] pb-4">
              <div className="w-10 h-10 rounded-full bg-[#FDF2F2] border border-[#F8B4B4] flex items-center justify-center text-[#C53030]">
                <AlertCircle className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-serif font-bold text-[#0F2744]">
                  Surveillance Desk Interface Exception
                </h2>
                <p className="text-xs text-[#64748B] font-sans">
                  An unexpected error occurred while rendering this surveillance view.
                </p>
              </div>
            </div>

            <div className="bg-[#F8FAFC] border border-[#CBD5E1] rounded-portal p-3.5 space-y-2 font-mono text-xs">
              <div className="text-[#C53030] font-bold break-words">
                {this.state.error?.name}: {this.state.error?.message || 'Unknown error'}
              </div>
              {this.state.errorInfo?.componentStack && (
                <details className="text-[10px] text-[#64748B] pt-1">
                  <summary className="cursor-pointer hover:text-[#0F2744]">View Component Stack</summary>
                  <pre className="mt-2 overflow-x-auto p-2 bg-slate-100 rounded text-[#334155] max-h-40 leading-snug">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={this.handleGoHome}
                className="px-4 py-2 rounded-portal border border-[#CBD5E1] text-[#0F2744] hover:bg-[#F1F4F9] text-xs font-mono font-medium flex items-center gap-1.5 cursor-pointer"
              >
                <Home className="w-3.5 h-3.5" />
                <span>Return to Home</span>
              </button>
              <button
                onClick={this.handleReset}
                className="px-4 py-2 rounded-portal bg-[#1B3A6B] hover:bg-[#0F2744] text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reload Workstation</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
