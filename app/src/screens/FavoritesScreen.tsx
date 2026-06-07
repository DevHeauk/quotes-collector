import React, {useState, useCallback, useEffect} from 'react';
import {View, FlatList, Text, StyleSheet, ActivityIndicator, TouchableOpacity, Alert} from 'react-native';
import {colors} from '../constants/colors';
import Icon from 'react-native-vector-icons/Ionicons';
import {fetchQuotesBatch} from '../api/client';
import {QuoteCard} from '../components/QuoteCard';
import {QuoteDetailView} from '../components/QuoteDetailView';
import {ResponsiveGrid} from '../components/ResponsiveGrid';
import {useResponsive} from '../hooks/useResponsive';
import {useFavorites} from '../hooks/useFavorites';
import {clearPreference} from '../storage/preferences';
import type {Quote} from '../types';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {useFocusEffect, CommonActions} from '@react-navigation/native';

export function FavoritesScreen({navigation}: {navigation: NativeStackNavigationProp<any>}) {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(true);
  const {ids, toggle, isFav} = useFavorites();
  const {isTablet} = useResponsive();
  const [selectedId, setSelectedId] = useState<string | null>(null);

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

  // 2-pane(태블릿)에서 선택 동기화: 펼침이면 첫 항목 자동 선택, 접힘이면 선택 해제.
  useEffect(() => {
    if (!isTablet) {
      setSelectedId(null);
      return;
    }
    if (quotes.length === 0) {
      setSelectedId(null);
    } else if (!selectedId || !quotes.some(q => q.id === selectedId)) {
      setSelectedId(quotes[0].id);
    }
  }, [isTablet, quotes, selectedId]);

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

  const header = (
    <TouchableOpacity style={styles.resetBtn} onPress={handleResetPreference}>
      <Text style={styles.resetText}>관심사 다시 설정</Text>
    </TouchableOpacity>
  );

  const empty = (
    <View style={styles.empty}>
      <Icon name="heart-outline" size={48} color={colors.heartInactive} />
      <Text style={styles.emptyText}>아직 좋아요한 명언이 없습니다.</Text>
      <Text style={styles.emptyHint}>마음에 드는 명언에 좋아요를 눌러보세요.</Text>
    </View>
  );

  // 태블릿/폴드 가로: 목록 + 상세 2-pane
  if (isTablet) {
    return (
      <View style={styles.twoPane}>
        <View style={styles.listPane}>
          <FlatList
            data={quotes}
            keyExtractor={item => item.id}
            contentContainerStyle={styles.listContent}
            ListHeaderComponent={header}
            renderItem={({item}) => (
              <View style={[styles.cell, selectedId === item.id && styles.cellSelected]}>
                <QuoteCard
                  quote={item}
                  isFavorite={isFav(item.id)}
                  onPress={() => setSelectedId(item.id)}
                  onToggleFavorite={() => toggle(item.id)}
                />
              </View>
            )}
            ListEmptyComponent={empty}
          />
        </View>
        <View style={styles.detailPane}>
          {selectedId ? (
            <QuoteDetailView
              quoteId={selectedId}
              onNavigateToQuote={setSelectedId}
              onAfterDelete={() => setSelectedId(null)}
            />
          ) : (
            <View style={styles.placeholder}>
              <Icon name="reader-outline" size={40} color={colors.textMuted} />
              <Text style={styles.placeholderText}>명언을 선택하세요</Text>
            </View>
          )}
        </View>
      </View>
    );
  }

  // 폰 / 폴드 커버 / 폴드 세로: 그리드 + 상세 화면 이동
  return (
    <ResponsiveGrid
      style={styles.container}
      data={quotes}
      keyExtractor={item => item.id}
      ListHeaderComponent={header}
      renderItem={({item}) => (
        <QuoteCard
          quote={item}
          isFavorite={isFav(item.id)}
          onPress={() => navigation.navigate('QuoteDetail', {quoteId: item.id})}
          onToggleFavorite={() => toggle(item.id)}
        />
      )}
      ListEmptyComponent={empty}
    />
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background},
  twoPane: {flex: 1, flexDirection: 'row', backgroundColor: colors.background},
  listPane: {width: 360, borderRightWidth: 1, borderRightColor: colors.border},
  listContent: {paddingHorizontal: 16, paddingBottom: 24},
  detailPane: {flex: 1},
  placeholder: {flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12},
  placeholderText: {color: colors.textMuted, fontSize: 15},
  cell: {borderRadius: 16, borderWidth: 2, borderColor: 'transparent'},
  cellSelected: {borderColor: colors.primary},
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
  emptyText: {color: colors.textSecondary, fontSize: 16, marginTop: 16},
  emptyHint: {color: colors.textMuted, fontSize: 13, marginTop: 8},
});
