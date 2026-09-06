// =============================================================
// MongoDB seed: supplier contract documents
// Executed via mongosh on first container start.
// =============================================================

db = db.getSiblingDB("hotel_enrichment");

db.supplier_contracts.drop();

db.supplier_contracts.insertMany([
  {
    supplier_id: "SUP-1",
    contract_start: "2025-06-01",
    contract_end: "2026-12-31",
    terms: {
      volume_discounts: [
        { min_quantity: 50,  discount_pct: 3.0 },
        { min_quantity: 100, discount_pct: 5.0 },
        { min_quantity: 200, discount_pct: 8.0 }
      ],
      delivery_sla_days: 5,
      allowed_categories: ["linens"]
    }
  },
  {
    supplier_id: "SUP-2",
    contract_start: "2025-09-01",
    contract_end: "2026-08-31",
    terms: {
      volume_discounts: [
        { min_quantity: 200, discount_pct: 4.0 },
        { min_quantity: 500, discount_pct: 7.0 }
      ],
      delivery_sla_days: 3,
      allowed_categories: ["toiletries"]
    }
  },
  {
    supplier_id: "SUP-3",
    contract_start: "2025-04-01",
    contract_end: "2027-03-31",
    terms: {
      volume_discounts: [
        { min_quantity: 20, discount_pct: 2.0 },
        { min_quantity: 50, discount_pct: 5.0 }
      ],
      delivery_sla_days: 7,
      allowed_categories: ["cleaning"]
    }
  },
  {
    supplier_id: "SUP-4",
    contract_start: "2025-01-01",
    contract_end: "2026-12-31",
    terms: {
      volume_discounts: [
        { min_quantity: 5, discount_pct: 10.0 }
      ],
      delivery_sla_days: 14,
      allowed_categories: ["equipment"]
    }
  },
  {
    supplier_id: "SUP-5",
    contract_start: "2025-11-01",
    contract_end: "2026-10-31",
    terms: {
      volume_discounts: [
        { min_quantity: 10, discount_pct: 3.0 },
        { min_quantity: 30, discount_pct: 6.0 }
      ],
      delivery_sla_days: 2,
      allowed_categories: ["food_bev"]
    }
  }
]);

print("Seeded supplier_contracts: " + db.supplier_contracts.countDocuments() + " documents");
