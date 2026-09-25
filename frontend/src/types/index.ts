// ==========================================
// 1. Enums & User Authorization
// ==========================================
export type RoleEnum = 'ADMIN' | 'WORKER'
export type CategoryEnum = 'WINDOW' | 'DOOR'
export type StatusEnum = 'DRAFT' | 'ISSUED'

export interface UserResponse {
  id: number
  username: string
  email?: string | null
  role: RoleEnum
  is_active: boolean
}

export interface UserRegister {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type?: string
}

// ==========================================
// 2. Aluminium Profiles (Catalog & Admin)
// ==========================================
export interface ProfileCreate {
  profile_name: string
  brand?: string | null
  gauge: number | string
  weight_per_meter: number | string
  rate_per_kg: number | string
}

export interface ProfileOut {
  id: number
  profile_name: string
  brand?: string | null
  gauge: string
  weight_per_meter: string
  rate_per_kg: string
  is_active: boolean
}
export interface ProfileUpdate {
  id:number
  profile_name?: string
  brand?: string | null
  gauge?: number | string
  weight_per_meter?: number | string
  rate_per_kg?: number | string
  is_active?: boolean
}

// ==========================================
// 3. Window & Door Types (Catalog & Admin)
// ==========================================
export interface TypeCreate {
  type_name: string
  category: CategoryEnum
  vertical_bars_count?: number
  horizontal_bars_count?: number
}

export interface TypeUpdate {
  type_name?: string
  category?: CategoryEnum
  vertical_bars_count?: number
  horizontal_bars_count?: number
  is_active?: boolean
}

export interface TypeOut {
  id: number
  type_name: string
  category: CategoryEnum
  vertical_bars_count: number
  horizontal_bars_count: number
  is_active: boolean
}

// ==========================================
// 4. Quotations & Price Calculation
// ==========================================
export interface PricePreviewRequest {
  aluminium_profile_id: number
  window_door_type_id: number
  height_mm: number
  width_mm: number
  quantity?: number
}

export interface PricePreviewResponse {
  frame_length_m: number
  calculated_weight_kg: number
  item_frame_cost: number
  price_per_unit: number
  item_total: number
}

export interface QuotationItemCreate {
  aluminium_profile_id: number
  window_door_type_id: number
  height_mm: number
  width_mm: number
  quantity?: number
}

export interface QuotationItemResponse {
  id: number
  aluminium_profile_id: number
  window_door_type_id: number
  width_mm: number
  height_mm: number
  quantity: number
  calculated_weight_kg: number
  item_frame_cost: number
  item_total: number
}

export interface CreateQuotationRequest {
  customer_name: string
  customer_phone?: string | null
  items: QuotationItemCreate[]
}

export interface QuotationResponse {
  id: number
  quotation_number: string
  customer_name: string
  worker_fee: number
  subtotal: number
  total_amount: number
  status: StatusEnum
  created_at: string
  items: QuotationItemResponse[]
}

// ==========================================
// 5. System Settings
// ==========================================
export interface SettingOut {
  key: string
  value: string
}