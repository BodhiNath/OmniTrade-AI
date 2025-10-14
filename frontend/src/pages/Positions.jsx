import { X, TrendingUp, TrendingDown } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const Positions = () => {
  const positions = [
    {
      symbol: 'AAPL',
      broker: 'Alpaca',
      side: 'LONG',
      qty: 10,
      entryPrice: 175.50,
      currentPrice: 178.45,
      pnl: 29.50,
      pnlPercent: 1.68,
      stopLoss: 173.00,
      takeProfit: 182.00,
      openTime: '2024-10-11 09:30'
    },
    {
      symbol: 'TSLA',
      broker: 'Alpaca',
      side: 'LONG',
      qty: 5,
      entryPrice: 245.00,
      currentPrice: 242.18,
      pnl: -14.10,
      pnlPercent: -1.15,
      stopLoss: 240.00,
      takeProfit: 255.00,
      openTime: '2024-10-11 10:15'
    },
    {
      symbol: 'BTC/USDT',
      broker: 'Binance',
      side: 'LONG',
      qty: 0.1,
      entryPrice: 43000.00,
      currentPrice: 43250.00,
      pnl: 25.00,
      pnlPercent: 0.58,
      stopLoss: 42500.00,
      takeProfit: 44000.00,
      openTime: '2024-10-11 08:45'
    },
  ]

  const PositionCard = ({ position }) => {
    const isProfitable = position.pnl >= 0

    return (
      <Card className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-2xl font-bold text-foreground">{position.symbol}</h3>
              <Badge variant={position.side === 'LONG' ? 'default' : 'destructive'}>
                {position.side}
              </Badge>
              <Badge variant="outline">{position.broker}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">Opened: {position.openTime}</p>
          </div>
          <Button variant="destructive" size="sm" className="gap-2">
            <X className="w-4 h-4" />
            Close Position
          </Button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <div className="text-sm text-muted-foreground mb-1">Quantity</div>
            <div className="text-lg font-semibold text-foreground">{position.qty}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground mb-1">Entry Price</div>
            <div className="text-lg font-semibold text-foreground">${position.entryPrice.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground mb-1">Current Price</div>
            <div className="text-lg font-semibold text-foreground">${position.currentPrice.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground mb-1">P&L</div>
            <div className={`text-lg font-semibold flex items-center gap-1 ${isProfitable ? 'text-green-600' : 'text-red-600'}`}>
              {isProfitable ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span>${Math.abs(position.pnl).toFixed(2)} ({position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%)</span>
            </div>
          </div>
        </div>

        <div className="flex gap-4 pt-4 border-t border-border">
          <div className="flex-1">
            <div className="text-sm text-muted-foreground mb-1">Stop Loss</div>
            <div className="text-lg font-semibold text-red-600">${position.stopLoss.toFixed(2)}</div>
          </div>
          <div className="flex-1">
            <div className="text-sm text-muted-foreground mb-1">Take Profit</div>
            <div className="text-lg font-semibold text-green-600">${position.takeProfit.toFixed(2)}</div>
          </div>
          <div className="flex-1">
            <div className="text-sm text-muted-foreground mb-1">Risk/Reward</div>
            <div className="text-lg font-semibold text-foreground">
              1:{((position.takeProfit - position.entryPrice) / (position.entryPrice - position.stopLoss)).toFixed(2)}
            </div>
          </div>
        </div>
      </Card>
    )
  }

  const totalPnL = positions.reduce((sum, pos) => sum + pos.pnl, 0)
  const totalValue = positions.reduce((sum, pos) => sum + (pos.qty * pos.currentPrice), 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Open Positions</h1>
          <p className="text-muted-foreground mt-1">Monitor and manage your active trades</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="text-sm text-muted-foreground mb-2">Total Positions</div>
          <div className="text-3xl font-bold text-foreground">{positions.length}</div>
        </Card>
        <Card className="p-6">
          <div className="text-sm text-muted-foreground mb-2">Total Value</div>
          <div className="text-3xl font-bold text-foreground">${totalValue.toFixed(2)}</div>
        </Card>
        <Card className="p-6">
          <div className="text-sm text-muted-foreground mb-2">Total P&L</div>
          <div className={`text-3xl font-bold ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)}
          </div>
        </Card>
      </div>

      {/* Positions List */}
      <div className="space-y-4">
        {positions.map((position, idx) => (
          <PositionCard key={idx} position={position} />
        ))}
      </div>

      {positions.length === 0 && (
        <Card className="p-12 text-center">
          <div className="text-muted-foreground">
            <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">No Open Positions</h3>
            <p>Your active positions will appear here when strategies execute trades.</p>
          </div>
        </Card>
      )}
    </div>
  )
}

export default Positions

