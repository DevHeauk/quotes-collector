import {useEffect, useRef} from 'react';
import {AppState} from 'react-native';
import {syncInteractions} from '../storage/interactions';

const SYNC_INTERVAL_MS = 5 * 60 * 1000; // 5분

export function useInteractionSync() {
  const lastSync = useRef(0);

  useEffect(() => {
    // 앱 시작 시 동기화
    syncInteractions();
    lastSync.current = Date.now();

    const sub = AppState.addEventListener('change', state => {
      if (state === 'active' && Date.now() - lastSync.current > SYNC_INTERVAL_MS) {
        syncInteractions();
        lastSync.current = Date.now();
      }
    });

    return () => sub.remove();
  }, []);
}
