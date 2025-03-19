export type Post = {
  account_display_name: string;
  account_profile_picture: string;
  account_username: string;
  content: string;
  created_at: string;
  id: number;
  is_owner: boolean;
  is_repost: boolean;
  type: string;
  url?: string;
  favorited: boolean;
  favorite_count: number;
  reposted: boolean;
  repost_count: number;
  reply_count: number;
  original_post?: Post;
  reply_to?: Post;
};
