import { BarChart3, Zap, Users, TrendingUp } from "lucide-react";

const Sidebar = () => {
  const stats = [
    { label: "Analyses", value: "1,247", icon: BarChart3 },
    { label: "Insights", value: "3,891", icon: Zap },
    { label: "Products", value: "892", icon: Users },
    { label: "Success Rate", value: "98.5%", icon: TrendingUp },
  ];

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
          Quick Stats
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
