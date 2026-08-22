export type BillStatus = 'draft' | 'posted' | 'partially_paid' | 'paid' | 'cancelled';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  organization_id: string;
  role_id: string;
  full_name: string;
  email: string | null;
  phone_number: string;
  is_active: boolean;
}

export interface LoginRequest {
  identifier?: string;
  email?: string;
  phone_number?: string;
  password: string;
  otp?: string;
  device_id?: string;
  device_name?: string;
}

export interface RegisterRequest {
  organization_name: string;
  full_name: string;
  email?: string;
  phone_number: string;
  password: string;
}

export interface BillItem {
  id?: string;
  description: string;
  quantity: string;
  unit: string;
  unit_price: string;
  discount_amount: string;
  tax_rate: string;
  tax_amount: string;
  line_total: string;
  hsn_code?: string | null;
}

export interface Bill {
  id: string;
  organization_id: string;
  supplier_id: string;
  bill_number: string;
  bill_date: string;
  due_date: string | null;
  subtotal: string;
  discount_amount: string;
  taxable_amount: string;
  cgst_amount: string;
  sgst_amount: string;
  igst_amount: string;
  total_amount: string;
  status: BillStatus;
  source_type: string;
  notes: string | null;
  items: BillItem[];
}

export interface BillCreate {
  supplier_id: string;
  bill_number: string;
  bill_date: string;
  due_date?: string | null;
  subtotal: string;
  discount_amount: string;
  taxable_amount: string;
  cgst_amount: string;
  sgst_amount: string;
  igst_amount: string;
  total_amount: string;
  notes?: string | null;
  items: Omit<BillItem, 'id'>[];
}

export interface ExtractedBillItem {
  description?: string | null;
  quantity?: string | null;
  unit?: string | null;
  unit_price?: string | null;
  discount_amount?: string | null;
  tax_rate?: string | null;
  tax_amount?: string | null;
  line_total?: string | null;
  hsn_code?: string | null;
}

export interface ExtractedBill {
  supplier_name?: string | null;
  supplier_gstin?: string | null;
  bill_number?: string | null;
  bill_date?: string | null;
  due_date?: string | null;
  subtotal?: string | null;
  discount_amount?: string | null;
  taxable_amount?: string | null;
  cgst_amount?: string | null;
  sgst_amount?: string | null;
  igst_amount?: string | null;
  total_amount?: string | null;
  items?: ExtractedBillItem[];
  confidence?: number;
  warnings?: string[];
}

export interface ScanConfirmResponse {
  supplier_match: {
    found: boolean;
    created: boolean;
    supplier_id: string;
    name: string;
    gstin: string | null;
  };
  bill: Bill;
}

export interface Payment {
  id: string;
  organization_id: string;
  supplier_id: string;
  amount: string;
  payment_method: string;
  payment_date: string;
  reference_number: string | null;
  cheque_number: string | null;
  cheque_date: string | null;
  bank_name: string | null;
  status: string;
  notes: string | null;
}

export interface PaymentCreate {
  supplier_id: string;
  amount: string;
  payment_method: string;
  payment_date: string;
  reference_number?: string | null;
  cheque_number?: string | null;
  cheque_date?: string | null;
  bank_name?: string | null;
  notes?: string | null;
}

export interface Supplier {
  id: string;
  name: string;
  contact_person: string | null;
  phone: string | null;
  email: string | null;
  gstin: string | null;
  address: string | null;
  payment_terms_days: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SupplierCreate {
  name: string;
  contact_person?: string | null;
  phone?: string | null;
  email?: string | null;
  gstin?: string | null;
  address?: string | null;
  payment_terms_days?: number;
}

export interface DashboardSummary {
  suppliers_count: number;
  bills_count: number;
  open_bills_count: number;
  payments_count: number;
  billed_amount: string;
  paid_amount: string;
  outstanding_amount: string;
  overdue_amount: string;
  due_soon_amount: string;
}

export interface DueReminder {
  bill_id: string;
  supplier_id: string;
  bill_number: string;
  due_date: string;
  days_until_due: number;
  outstanding_amount: string;
}

export interface Attachment {
  id: string;
  organization_id: string;
  entity_type: string;
  entity_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  uploaded_by: string;
  created_at: string;
}

export interface PaymentScanConfirmResponse {
  payment_id: string;
  supplier_id: string;
  supplier_name: string;
  amount: string;
  allocated_amount: string;
  unallocated_amount: string;
  allocations: {
    bill_id: string;
    bill_number: string;
    amount: string;
    bill_status: string;
    outstanding_after: string;
  }[];
}

export interface ExtractedPayment {
  supplier_name?: string | null;
  supplier_id?: string | null;
  amount?: string | null;
  payment_method?: string;
  payment_date?: string | null;
  reference_number?: string | null;
  paid_at?: string | null;
  confidence?: number;
  warnings?: string[];
}

export interface ApiError {
  detail: string;
}
