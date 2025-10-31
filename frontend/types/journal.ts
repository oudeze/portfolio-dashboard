/**
 * Journal and P&L types matching backend models.
 */

export interface JournalEntry {
  id: string;
  ts: string;
  symbol: string;
  side: 'buy' | 'sell';
  qty: number;
  price: number;
  notes?: string;
}

export interface CreateJournalEntryRequest {
  symbol: string;
  side: 'buy' | 'sell';
  qty: number;
  price: number;
  notes?: string;
}

export interface PnLSummary {
  symbol: string;
  qty: number;
  avg_price: number;
  current_price: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
}

