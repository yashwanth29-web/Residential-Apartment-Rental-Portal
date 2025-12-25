export interface Tower {
  id: number;
  name: string;
  address: string;
  total_floors: number;
  flats_per_floor: number;
  amenities?: Amenity[];
  amenity_ids?: number[];
}

export interface Amenity {
  id: number;
  name: string;
  type: 'gym' | 'pool' | 'parking' | 'common';
  description: string | null;
  hours: string | null;
  fee: number | null;
}

export interface Flat {
  id: number;
  tower_id: number;
  tower_name: string;
  unit_number: string;
  floor: number;
  bedrooms: number;
  bathrooms: number;
  area_sqft: number | null;
  rent: number;
  is_available: boolean;
  created_at: string;
}

export interface FlatFilter {
  tower_id?: number;
  bedrooms?: number;
  min_rent?: number;
  max_rent?: number;
}
