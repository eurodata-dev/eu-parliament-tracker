export type Position = "FOR" | "AGAINST" | "ABSTENTION" | "DID_NOT_VOTE";

export type Tally = Record<Position, number>;

export interface Country {
  code: string;
  iso_alpha_2: string;
  label: string;
}

export interface Group {
  code: string;
  label: string;
  short_label: string;
}

export interface Topic {
  code: string;
  label: string;
}

export interface Member {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  country: Country;
  group: Group | null;
  national_party: { id: string; label: string; short_label: string } | null;
  photo_url: string | null;
  thumb_url: string | null;
}

export interface MemberProfile extends Member {
  date_of_birth: string | null;
  terms: number[];
  email: string | null;
  facebook: string | null;
  twitter: string | null;
}

export interface VoteSummary {
  id: string;
  timestamp: string;
  display_title: string;
  description: string | null;
  reference: string | null;
  result: "ADOPTED" | "REJECTED" | null;
  topics: Topic[];
  geo_areas: { code: string; iso_alpha_2: string; label: string }[];
  responsible_committees: { code: string; label: string; abbreviation: string }[];
  amendment_subject: string | null;
  amendment_number: string | null;
}

export interface VoteDetail extends VoteSummary {
  document: { type: string; reference: string; url: string } | null;
  procedure: { title: string; type: string; reference: string; url: string } | null;
  snippet: { text: string; source_type: string; source_url: string } | null;
  stats: {
    total: Tally;
    by_group: { group: Group; stats: Tally }[];
    by_country: { country: Country; stats: Tally }[];
  };
  member_votes: { member: Member; position: Position }[];
}

export interface MemberVote extends VoteSummary {
  position: Position;
}

export interface Page<T> {
  total: number;
  page: number;
  page_size: number;
  has_prev: boolean;
  has_next: boolean;
  results: T[];
}
