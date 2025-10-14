import { useState } from 'react'
import { Play, Pause, Settings, TrendingUp, Plus } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const Strategies = () => {
  const [strategies, setStrategies] = useState([
    {
      id: 1,
      name: 'RSI Momentum',
      type: 'Technical',
      status: 'active',
      broker: 'Alpaca',
      symbols: ['AAPL', 'TSLA', 'MSFT'],
      performance: {
        trades: 45,
        winRate: 68.5,
        pnl: 1245.67,
        avgReturn: 2.4
      }
    },
    {
      id: 2,
      name: 'MACD Crossover',
      type: 'Technical',
      status: 'active',
      broker: 'Alpaca',
      symbols: ['SPY', 'QQQ'],
      performance: {
        trades: 32,
        winRate: 71.2,
        pnl: 892.34,
        avgReturn: 1.8
      }
    },
    {
      id: 3,
      name: 'Crypto Scalper',
      type: 'Technical',
      status: 'paused',
      broker: 'Binance',
      symbols: ['BTC/USDT', 'ETH/USDT'],
      performance: {
        trades: 128,
        winRate: 62.3,
        pnl: 2145.89,
        avgReturn: 0.8
      }
    },
  ])

  const StrategyCard = ({ strategy }) => (
    <Card className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-bold text-foreground">{strategy.name}</h3>
            <Badge variant={strategy.status === 'active' ? 'default' : 'secondary'}>
              {strategy.status}
            </Badge>
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>{strategy.type}</span>
            <span>•</span>
            <span>{strategy.broker}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            size="icon"
            variant="outline"
            onClick={() => {
              const updated = strategies.map(s =>
                s.id === strategy.id
                  ? { ...s, status: s.status === 'active' ? 'paused' : 'active' }
                  : s
              )
              setStrategies(updated)
            }}
          >
            {strategy.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>
          <Button size="icon" variant="outline">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-muted-foreground mb-2">Trading Symbols</div>
        <div className="flex flex-wrap gap-2">
          {strategy.symbols.map((symbol, idx) => (
            <Badge key={idx} variant="outline">{symbol}</Badge>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 pt-4 border-t border-border">
        <div>
          <div className="text-sm text-muted-foreground mb-1">Trades</div>
          <div className="text-lg font-semibold text-foreground">{strategy.performance.trades}</div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground mb-1">Win Rate</div>
          <div className="text-lg font-semibold text-green-600">{strategy.performance.winRate}%</div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground mb-1">P&L</div>
          <div className={`text-lg font-semibold ${strategy.performance.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${strategy.performance.pnl.toFixed(2)}
          </div>
        </div>
        <div>
          <div className="text-sm text-muted-foreground mb-1">Avg Return</div>
          <div className="text-lg font-semibold text-foreground">{strategy.performance.avgReturn}%</div>
        </div>
      </div>
    </Card>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Trading Strategies</h1>
          <p className="text-muted-foreground mt-1">Manage and monitor your automated trading strategies</p>
        </div>
        <Button className="gap-2">
          <Plus className="w-4 h-4" />
          New Strategy
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {strategies.map(strategy => (
          <StrategyCard key={strategy.id} strategy={strategy} />
        ))}
      </div>

      {/* Strategy Templates */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Strategy Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { name: 'Bollinger Bands Breakout', description: 'Trade breakouts using Bollinger Bands volatility' },
            { name: 'Moving Average Crossover', description: 'Classic MA crossover strategy with customizable periods' },
            { name: 'Mean Reversion', description: 'Profit from price returning to statistical mean' },
          ].map((template, idx) => (
            <Card key={idx} className="p-4 border-2 border-dashed border-muted hover:border-primary cursor-pointer transition-colors">
              <div className="flex items-start gap-3">
                <TrendingUp className="w-5 h-5 text-primary mt-1" />
                <div>
                  <h3 className="font-semibold text-foreground mb-1">{template.name}</h3>
                  <p className="text-sm text-muted-foreground">{template.description}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </Card>
    </div>
  )
}

export default Strategies

