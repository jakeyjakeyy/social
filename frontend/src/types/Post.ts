export type Post = {
  account_display_name: string;
  account_username: string;
  content: string;
  created_at: string;
  favorite_count: number;
  favorited: boolean;
  id: number;
  is_owner: boolean;
  is_repost: boolean;
  original_post: Post | null;
  repost_count: number;
  reposted: boolean;
  type: string;
  url: string;
};
