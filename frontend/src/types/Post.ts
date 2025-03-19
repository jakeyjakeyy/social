export interface Post {
  id: number;
  content: string;
  created_at: string;
  type: string;
  url?: string;
  account_username: string;
  account_display_name: string;
  account_avatar: string;
  is_owner: boolean;
  favorited: boolean;
  favorite_count: number;
  reposted: boolean;
  repost_count: number;
  reply_count: number;
  is_repost: boolean;
  original_post?: Post;
  reply_to?: Post;
}
