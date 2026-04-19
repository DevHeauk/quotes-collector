import {useEffect, useRef, useState} from 'react';
import {API_BASE_URL} from '../constants/config';
import {getDeviceId} from '../storage/deviceId';

export interface UserProfile {
  keyword_weights: Record<string, number>;
  situation_weights: Record<string, number>;
  total_interactions: number;
  profile_strength: 'weak' | 'moderate' | 'strong';
}

export function useProfile() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const fetched = useRef(false);

  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;

    getDeviceId().then(deviceId =>
      fetch(`${API_BASE_URL}/app/api/v1/profile?device_id=${deviceId}`)
        .then(r => r.ok ? r.json() : null)
        .then(setProfile)
        .catch(() => {}),
    );
  }, []);

  return profile;
}
