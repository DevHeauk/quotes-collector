import React, {useEffect, useState, useCallback} from 'react';
import {View, FlatList, StyleSheet, ActivityIndicator, Text} from 'react-native';
import {colors} from '../constants/colors';
import {fetchQuotes} from '../api/client';
import {QuoteCard} from '../components/QuoteCard';
import {useFavorites} from '../hooks/useFavorites';
import type {Quote} from '../types';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';
import type {RouteProp} from '@react-navigation/native';

type Props = {
  navigation: NativeStackNavigationProp<any>;
  route: RouteProp<{QuoteList: {title: string; filter: Record<string, string>}}, 'QuoteList'>;
};

export function QuoteListScreen({navigation, route}: Props) {
  const {title, filter} = route.params;
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const {toggle, isFav} = useFavorites();

  React.useLayoutEffect(() => {
    navigation.setOptions({title});
  }, [navigation, title]);

  const load = useCallback(async (p: number) => {
    const data = await fetchQuotes({...filter, page: String(p), limit: '20'});
    if (p === 1) {
      setQuotes(data);
    } else {
      setQuotes(prev => [...prev, ...data]);
    }
    setHasMore(data.length === 20);
    setLoading(false);
  }, [filter]);

  useEffect(() => {
    load(1);
  }, [load]);

  const loadMore = () => {
    if (!hasMore || loading) return;
    const next = page + 1;
    setPage(next);
    load(next);
  };

  if (loading && quotes.length === 0) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <FlatList
      style={styles.container}
      data={quotes}
      keyExtractor={item => item.id}
      renderItem={({item}) => (
        <QuoteCard
          quote={item}
          isFavorite={isFav(item.id)}
          onPress={() => navigation.navigate('QuoteDetail', {quoteId: item.id})}
          onToggleFavorite={() => toggle(item.id)}
        />
      )}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
      ListEmptyComponent={<Text style={styles.empty}>명언이 없습니다.</Text>}
      ListFooterComponent={hasMore ? <ActivityIndicator color={colors.primary} style={{padding: 16}} /> : null}
    />
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background},
  empty: {color: colors.textMuted, textAlign: 'center', marginTop: 40, fontSize: 16},
});
