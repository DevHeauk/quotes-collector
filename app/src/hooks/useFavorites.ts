import {useState, useEffect, useCallback} from 'react';
import {getFavorites, addFavorite, removeFavorite} from '../storage/favorites';
import {logInteraction} from '../storage/interactions';

export function useFavorites() {
  const [ids, setIds] = useState<string[]>([]);

  useEffect(() => {
    getFavorites().then(setIds);
  }, []);

  const toggle = useCallback(async (id: string) => {
    if (ids.includes(id)) {
      await removeFavorite(id);
      setIds(prev => prev.filter(x => x !== id));
      logInteraction({quote_id: id, type: 'unlike'});
    } else {
      await addFavorite(id);
      setIds(prev => [id, ...prev]);
      logInteraction({quote_id: id, type: 'like'});
    }
  }, [ids]);

  const isFav = useCallback((id: string) => ids.includes(id), [ids]);

  return {ids, toggle, isFav};
}
