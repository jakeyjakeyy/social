export type Post = {
  id: number;
  account_display_name: string;
  account_username: string;
  created_at: string;
  content: string;
  favorited: boolean;
  favorite_count: number;
  reposted: boolean;
  repost_count: number;
  type: string;
  is_owner: boolean;
};
