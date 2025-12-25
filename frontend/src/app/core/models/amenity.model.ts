export type AmenityType = 'gym' | 'pool' | 'parking' | 'common';

export interface Amenity {
  id: number;
  name: string;
  type: AmenityType;
  description: string | null;
  hours: string | null;
  fee: number | null;
}
