import React, {useEffect, useState, useCallback} from 'react';
import {View, FlatList, Text, StyleSheet, ActivityIndicator, TouchableOpacity, Alert} from 'react-native';
import {colors} from '../constants/colors';
import {fetchQuotesBatch} from '../api/client';
import {QuoteCard} from '../components/QuoteCard';
import {useFavorites} from '../hooks/useFavorites';
import {clearPreference} from '../storage/preferences';
import type {Quote} from '../types';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {useFocusEffect, CommonActions} from '@react-navigation/native';

export function FavoritesScreen({navigation}: {navigation: NativeStackNavigationProp<any>}) {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(true);
  const {ids, toggle, isFav} = useFavorites();

  useFocusEffect(
    useCallback(() => {
      if (ids.length === 0) {
        setQuotes([]);
        setLoading(false);
        return;
      }
      setLoading(true);
      fetchQuotesBatch(ids)
        .then(data => {
          const sorted = ids.map(id => data.find(q => q.id === id)).filter(Boolean) as Quote[];
          setQuotes(sorted);
        })
        .catch(console.error)
        .finally(() => setLoading(false));
    }, [ids])
  );

  const handleResetPreference = () => {
    Alert.alert(
      '관심사 다시 설정',
      '온보딩을 다시 진행하시겠습니까?\n좋아요 목록은 유지됩니다.',
      [
        {text: '취소', style: 'cancel'},
        {
          text: '다시 설정',
          onPress: async () => {
            await clearPreference();
            navigation.dispatch(
              CommonActions.reset({index: 0, routes: [{name: 'SituationPicker'}]}),
            );
          },
        },
      ],
    );
  };

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
  }

  return (
    <FlatList
      style={styles.container}
      data={quotes}
      keyExtractor={item => item.id}
      ListHeaderComponent={
        <TouchableOpacity style={styles.resetBtn} onPress={handleResetPreference}>
          <Text style={styles.resetText}>관심사 다시 설정</Text>
        </TouchableOpacity>
      }
      renderItem={({item}) => (
        <QuoteCard
          quote={item}
          isFavorite={isFav(item.id)}
          onPress={() => navigation.navigate('QuoteDetail', {quoteId: item.id})}
          onToggleFavorite={() => toggle(item.id)}
        />
      )}
      ListEmptyComponent={
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>♡</Text>
          <Text style={styles.emptyText}>아직 좋아요한 명언이 없습니다.</Text>
          <Text style={styles.emptyHint}>마음에 드는 명언에 ♥를 눌러보세요.</Text>
        </View>
      }
    />
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background},
  resetBtn: {
    alignSelf: 'flex-end',
    marginHorizontal: 16,
    marginTop: 12,
    marginBottom: 4,
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: colors.surface,
    borderRadius: 10,
  },
  resetText: {color: colors.textSecondary, fontSize: 13},
  empty: {alignItems: 'center', marginTop: 80},
  emptyIcon: {fontSize: 48, color: colors.heartInactive},
  emptyText: {color: colors.textSecondary, fontSize: 16, marginTop: 16},
  emptyHint: {color: colors.textMuted, fontSize: 13, marginTop: 8},
});
