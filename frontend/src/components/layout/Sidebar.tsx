import { BarChart3, TrendingUp, Clock, Activity } from "lucide-react";
import { useState, useEffect } from "react";

interface SystemStats {
  uptime_percentage: number;
  avg_response_time: number;
  cache_hit_rate: number;
  api_calls: number;
}

const Sidebar = () => {
  const [stats, setStats] = useState([
    { label: "Uptime", value: "Loading...", icon: TrendingUp },
    { label: "Avg Response", value: "Loading...", icon: Clock },
    { label: "Cache Hit Rate", value: "Loading...", icon: BarChart3 },
    { label: "API Calls", value: "Loading...", icon: Activity },
  ]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/system-stats`);
        if (!response.ok) {
          throw new Error('Failed to fetch stats');
        }
        const data: SystemStats = await response.json();
        
        setStats([
          { label: "Uptime", value: `${data.uptime_percentage}%`, icon: TrendingUp },
          { label: "Avg Response", value: `${data.avg_response_time}s`, icon: Clock },
          { label: "Cache Hit Rate", value: `${data.cache_hit_rate}%`, icon: BarChart3 },
          { label: "API Calls", value: data.api_calls.toString(), icon: Activity },
        ]);
      } catch (error) {
        console.error('Failed to fetch system stats:', error);
        // Keep loading state or show error state
        setStats([
          { label: "Uptime", value: "N/A", icon: TrendingUp },
          { label: "Avg Response", value: "N/A", icon: Clock },
          { label: "Cache Hit Rate", value: "N/A", icon: BarChart3 },
          { label: "API Calls", value: "N/A", icon: Activity },
        ]);
      }
    };

    // Initial fetch
    fetchStats();
    
    // Update every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <BarChart3 className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">MarketPro</h1>
            <p className="text-xs text-gray-400">Analytics Suite</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-6">
        <div className="space-y-4">
          <div>
            <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">
              Analytics
            </h3>
            <ul className="space-y-1">
              <li>
                <a
                  href="#"
                  className="flex items-center px-3 py-2 text-sm font-medium text-primary-400 bg-primary-500/10 rounded-lg"
                >
                  <BarChart3 className="mr-3 h-4 w-4" />
                  Dashboard
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* Stats */}
      <div className="p-6 border-t border-gray-800">
        <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">
          System Health
        </h3>
        <div className="space-y-3">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Icon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-300">{stat.label}</span>
                </div>
                <span className="text-sm font-medium text-white">
                  {stat.value}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
