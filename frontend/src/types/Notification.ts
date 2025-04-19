export type Notification = {
  action: string;
  action_account: string;
  action_account_displayname: string;
  read: boolean;
  created_at: string;
  post_id: number | null;
  notification_id: number;
};
