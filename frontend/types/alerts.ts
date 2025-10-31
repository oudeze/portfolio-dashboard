/**
 * Alert types matching backend models.
 */

export interface AlertRule {
  id: string;
  symbol: string;
  kind: 'price_above' | 'price_below' | 'pct_move';
  threshold: number;
  enabled: boolean;
}

export interface CreateAlertRequest {
  symbol: string;
  kind: 'price_above' | 'price_below' | 'pct_move';
  threshold: number;
  enabled?: boolean;
}

