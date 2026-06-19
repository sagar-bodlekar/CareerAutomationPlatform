import { useState, useEffect } from "react";
import { WifiOff, Wifi, RefreshCw } from "lucide-react";
import { useNetworkStatus } from "../../hooks/useNetworkStatus";

export default function OfflineBanner() {
  const { isOnline, wasOffline } = useNetworkStatus();
  const [showReconnected, setShowReconnected] = useState(false);

  useEffect(() => {
    if (isOnline && wasOffline) {
      setShowReconnected(true);
      const timer = setTimeout(() => setShowReconnected(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [isOnline, wasOffline]);

  const handleRefresh = () => {
    window.location.reload();
  };

  if (!isOnline) {
    return (
      <div className="sticky top-0 z-50 flex items-center justify-center gap-2 bg-amber-500 px-4 py-2 text-sm font-medium text-white shadow-sm">
        <WifiOff className="h-4 w-4 shrink-0" />
        <span>You are offline. Some features may be unavailable.</span>
        <span className="ml-2 text-xs opacity-75">Reconnecting...</span>
      </div>
    );
  }

  if (showReconnected) {
    return (
      <div className="sticky top-0 z-50 flex items-center justify-center gap-2 bg-green-500 px-4 py-2 text-sm font-medium text-white shadow-sm animate-fade-in">
        <Wifi className="h-4 w-4 shrink-0" />
        <span>Back online</span>
        <button
          onClick={handleRefresh}
          className="ml-2 flex items-center gap-1 rounded bg-white/20 px-2 py-0.5 text-xs hover:bg-white/30 transition-colors"
        >
          <RefreshCw className="h-3 w-3" />
          Refresh data
        </button>
      </div>
    );
  }

  return null;
}
