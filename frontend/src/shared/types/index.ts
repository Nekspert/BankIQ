export interface UserProfile {
  imageUrl: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  isStaff: boolean;
  isSuperuser: boolean;
  profile: UserProfile;
}