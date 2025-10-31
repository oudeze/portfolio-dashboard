/**
 * Market data types matching backend models.
 */

export interface Symbol {
  symbol: string;
  name?: string;
  asset_type: string;
}

export interface Quote {
  symbol: string;
  price: number;
  ts: string;
}

