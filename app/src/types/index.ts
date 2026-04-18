export interface Author {
  id?: string;
  name: string;
  profession: string;
  field: string;
  nationality: string;
  birth_year: number | null;
}

export interface Quote {
  id: string;
  text: string;
  text_original?: string;
  original_language?: string;
  source?: string;
  year?: number;
  impact_score?: number;
  keywords: string[];
  situations?: string[];
  author: Author;
  author_name?: string;
  related_quotes?: {id: string; text: string; impact_score: number}[];
}

export interface CategoryGroup {
  group_name: string;
  count: number;
  keywords: string[];
}

export interface SituationGroup {
  group_name: string;
  count: number;
  situations: string[];
}

export interface AuthorListItem {
  id: string;
  name: string;
  profession: string;
  field: string;
  nationality: string;
  birth_year: number | null;
  quote_count: number;
}
