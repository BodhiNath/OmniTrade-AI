import { useState } from 'react'
import { Save, AlertTriangle } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'

const Settings = () => {
  const [settings, setSettings] = useState({
    enableTrading: false,
    alpacaLiveMode: false,
    binanceTestnet: true,
    maxPositionSize: 5.0,
    defaultStopLoss: 2.0,
    dailyLossLimit: 10.0,
    maxConsecutiveLosses: 5,
    alpacaApiKey: '••••••••••••••••',
    alpacaSecretKey: '••••••••••••••••',
    binanceApiKey: '••••••••••••••••',
    binanceSecretKey: '••••••••••••••••',
    telegramBotToken: '',
    telegramChatId: '',
  })

  const handleSave = () => {
    alert('Settings saved successfully!')
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-1">Configure your trading system and risk parameters</p>
      </div>

      {/* Trading Controls */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Trading Controls</h2>
        
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Enable Trading</Label>
              <p className="text-sm text-muted-foreground">Master switch to enable/disable all trading</p>
            </div>
            <Switch
              checked={settings.enableTrading}
              onCheckedChange={(checked) => setSettings({ ...settings, enableTrading: checked })}
            />
          </div>

          {settings.enableTrading && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-500 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 dark:text-red-100">Live Trading Enabled</h3>
                  <p className="text-sm text-red-800 dark:text-red-200">
                    Real trades will be executed. Ensure you understand all risks before proceeding.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Alpaca Live Mode</Label>
              <p className="text-sm text-muted-foreground">Use live account instead of paper trading</p>
            </div>
            <Switch
              checked={settings.alpacaLiveMode}
              onCheckedChange={(checked) => setSettings({ ...settings, alpacaLiveMode: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Binance Testnet</Label>
              <p className="text-sm text-muted-foreground">Use testnet for crypto trading</p>
            </div>
            <Switch
              checked={settings.binanceTestnet}
              onCheckedChange={(checked) => setSettings({ ...settings, binanceTestnet: checked })}
            />
          </div>
        </div>
      </Card>

      {/* Risk Management */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Risk Management</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label htmlFor="maxPosition">Max Position Size (%)</Label>
            <Input
              id="maxPosition"
              type="number"
              step="0.1"
              value={settings.maxPositionSize}
              onChange={(e) => setSettings({ ...settings, maxPositionSize: parseFloat(e.target.value) })}
            />
            <p className="text-sm text-muted-foreground">Maximum percentage of portfolio per trade</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="stopLoss">Default Stop Loss (%)</Label>
            <Input
              id="stopLoss"
              type="number"
              step="0.1"
              value={settings.defaultStopLoss}
              onChange={(e) => setSettings({ ...settings, defaultStopLoss: parseFloat(e.target.value) })}
            />
            <p className="text-sm text-muted-foreground">Default stop loss percentage</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="dailyLimit">Daily Loss Limit (%)</Label>
            <Input
              id="dailyLimit"
              type="number"
              step="0.1"
              value={settings.dailyLossLimit}
              onChange={(e) => setSettings({ ...settings, dailyLossLimit: parseFloat(e.target.value) })}
            />
            <p className="text-sm text-muted-foreground">Maximum daily loss before halting</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="consecutiveLosses">Max Consecutive Losses</Label>
            <Input
              id="consecutiveLosses"
              type="number"
              value={settings.maxConsecutiveLosses}
              onChange={(e) => setSettings({ ...settings, maxConsecutiveLosses: parseInt(e.target.value) })}
            />
            <p className="text-sm text-muted-foreground">Pause trading after N losses</p>
          </div>
        </div>
      </Card>

      {/* Broker API Keys */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Broker API Keys</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold text-foreground mb-4">Alpaca</h3>
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label htmlFor="alpacaKey">API Key</Label>
                <Input
                  id="alpacaKey"
                  type="password"
                  value={settings.alpacaApiKey}
                  onChange={(e) => setSettings({ ...settings, alpacaApiKey: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="alpacaSecret">Secret Key</Label>
                <Input
                  id="alpacaSecret"
                  type="password"
                  value={settings.alpacaSecretKey}
                  onChange={(e) => setSettings({ ...settings, alpacaSecretKey: e.target.value })}
                />
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-foreground mb-4">Binance</h3>
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label htmlFor="binanceKey">API Key</Label>
                <Input
                  id="binanceKey"
                  type="password"
                  value={settings.binanceApiKey}
                  onChange={(e) => setSettings({ ...settings, binanceApiKey: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="binanceSecret">Secret Key</Label>
                <Input
                  id="binanceSecret"
                  type="password"
                  value={settings.binanceSecretKey}
                  onChange={(e) => setSettings({ ...settings, binanceSecretKey: e.target.value })}
                />
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Notifications */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Notifications</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold text-foreground mb-4">Telegram</h3>
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label htmlFor="telegramBot">Bot Token</Label>
                <Input
                  id="telegramBot"
                  type="password"
                  placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                  value={settings.telegramBotToken}
                  onChange={(e) => setSettings({ ...settings, telegramBotToken: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="telegramChat">Chat ID</Label>
                <Input
                  id="telegramChat"
                  placeholder="123456789"
                  value={settings.telegramChatId}
                  onChange={(e) => setSettings({ ...settings, telegramChatId: e.target.value })}
                />
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end gap-3">
        <Button variant="outline">Reset to Defaults</Button>
        <Button onClick={handleSave} className="gap-2">
          <Save className="w-4 h-4" />
          Save Settings
        </Button>
      </div>
    </div>
  )
}

export default Settings

