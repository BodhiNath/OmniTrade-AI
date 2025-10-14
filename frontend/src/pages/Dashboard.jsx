import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertCircle } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const Dashboard = () => {
  const [systemStatus, setSystemStatus] = useState('active')
  const [stats, setStats] = useState({
    totalPnL: 2450.32,
    dailyPnL: 145.67,
    winRate: 68.5,
    activePositions: 5,
  })

  // Mock performance data
  const performanceData = [
    { date: '10/01', value: 10000 },
    { date: '10/02', value: 10150 },
    { date: '10/03', value: 10080 },
    { date: '10/04', value: 10320 },
    { date: '10/05', value: 10280 },
    { date: '10/06', value: 10450 },
    { date: '10/07', value: 10520 },
  ]

  const StatCard = ({ title, value, change, icon: Icon, trend }) => (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-muted-foreground">{title}</span>
        <Icon className="w-5 h-5 text-muted-foreground" />
      </div>
      <div className="space-y-1">
        <div className="text-3xl font-bold text-foreground">{value}</div>
        <div className={`flex items-center gap-1 text-sm ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span>{change}</span>
        </div>
      </div>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Warning Banner */}
      <Card className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-500 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">Paper Trading Mode</h3>
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              You are currently in paper trading mode. No real money is at risk. Enable live trading in Settings when ready.
            </p>
          </div>
        </div>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total P&L"
          value={`$${stats.totalPnL.toFixed(2)}`}
          change="+12.4%"
          icon={DollarSign}
          trend="up"
        />
        <StatCard
          title="Daily P&L"
          value={`$${stats.dailyPnL.toFixed(2)}`}
          change="+5.2%"
          icon={TrendingUp}
          trend="up"
        />
        <StatCard
          title="Win Rate"
          value={`${stats.winRate}%`}
          change="+2.1%"
          icon={Activity}
          trend="up"
        />
        <StatCard
          title="Active Positions"
          value={stats.activePositions}
          change="2 new"
          icon={Activity}
          trend="up"
        />
      </div>

      {/* Performance Chart */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-foreground">Portfolio Performance</h2>
            <p className="text-sm text-muted-foreground">Last 7 days</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">7D</Button>
            <Button variant="outline" size="sm">1M</Button>
            <Button variant="outline" size="sm">3M</Button>
            <Button variant="outline" size="sm">1Y</Button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={performanceData}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="date" className="text-xs" />
            <YAxis className="text-xs" />
            <Tooltip />
            <Area type="monotone" dataKey="value" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorValue)" />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Recent Trades */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Recent Trades</h2>
        <div className="space-y-3">
          {[
            { symbol: 'AAPL', type: 'BUY', price: 178.45, qty: 10, pnl: 45.20, time: '2 min ago' },
            { symbol: 'TSLA', type: 'SELL', price: 242.18, qty: 5, pnl: -12.50, time: '15 min ago' },
            { symbol: 'BTC/USD', type: 'BUY', price: 43250.00, qty: 0.1, pnl: 125.00, time: '1 hour ago' },
          ].map((trade, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className={`px-3 py-1 rounded text-xs font-semibold ${
                  trade.type === 'BUY' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 
                  'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                }`}>
                  {trade.type}
                </div>
                <div>
                  <div className="font-semibold text-foreground">{trade.symbol}</div>
                  <div className="text-sm text-muted-foreground">{trade.qty} @ ${trade.price}</div>
                </div>
              </div>
              <div className="text-right">
                <div className={`font-semibold ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                </div>
                <div className="text-sm text-muted-foreground">{trade.time}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* System Controls */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">System Controls</h2>
        <div className="flex gap-3">
          <Button className="bg-green-600 hover:bg-green-700">
            Start Trading Engine
          </Button>
          <Button variant="destructive">
            Emergency Stop
          </Button>
          <Button variant="outline">
            Reset Daily Stats
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default Dashboard

