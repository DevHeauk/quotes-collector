import React, {useEffect, useState, useCallback} from 'react';
import {View, FlatList, Text, TextInput, StyleSheet, ActivityIndicator, TouchableOpacity, Alert} from 'react-native';
import {colors} from '../constants/colors';
import Icon from 'react-native-vector-icons/Ionicons';
import {fetchQuotesBatch} from '../api/client';
import {QuoteCard} from '../components/QuoteCard';
import {useFavorites} from '../hooks/useFavorites';
import {clearPreference} from '../storage/preferences';
import {getAdminToken, setAdminToken, clearAdminToken} from '../storage/admin';
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

  const [isAdmin, setIsAdmin] = useState(false);
  const [tokenInput, setTokenInput] = useState('');
  const [showTokenInput, setShowTokenInput] = useState(false);

  useEffect(() => {
    getAdminToken().then(t => setIsAdmin(!!t));
  }, []);

  const handleAdminToggle = () => {
    if (isAdmin) {
      Alert.alert('관리자 모드 해제', '관리자 모드를 해제하시겠습니까?', [
        {text: '취소', style: 'cancel'},
        {text: '해제', onPress: async () => {
          await clearAdminToken();
          setIsAdmin(false);
        }},
      ]);
    } else {
      setShowTokenInput(true);
    }
  };

  const handleTokenSubmit = async () => {
    if (tokenInput.trim()) {
      await setAdminToken(tokenInput.trim());
      setIsAdmin(true);
      setShowTokenInput(false);
      setTokenInput('');
    }
  };

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
        <View>
          <View style={styles.headerRow}>
            <TouchableOpacity style={styles.resetBtn} onPress={handleResetPreference}>
              <Text style={styles.resetText}>관심사 다시 설정</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.resetBtn, isAdmin && styles.adminActiveBtn]}
              onPress={handleAdminToggle}>
              <Text style={[styles.resetText, isAdmin && styles.adminActiveText]}>
                {isAdmin ? '관리자 ON' : '관리자'}
              </Text>
            </TouchableOpacity>
          </View>
          {showTokenInput && (
            <View style={styles.tokenRow}>
              <TextInput
                style={styles.tokenInput}
                placeholder="관리자 토큰 입력"
                placeholderTextColor={colors.textMuted}
                value={tokenInput}
                onChangeText={setTokenInput}
                secureTextEntry
                autoFocus
              />
              <TouchableOpacity style={styles.tokenSubmitBtn} onPress={handleTokenSubmit}>
                <Text style={styles.tokenSubmitText}>확인</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
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
          <Icon name="heart-outline" size={48} color={colors.heartInactive} />
          <Text style={styles.emptyText}>아직 좋아요한 명언이 없습니다.</Text>
          <Text style={styles.emptyHint}>마음에 드는 명언에 좋아요를 눌러보세요.</Text>
        </View>
      }
    />
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background},
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginHorizontal: 16,
    marginTop: 12,
    marginBottom: 4,
  },
  resetBtn: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: colors.surface,
    borderRadius: 10,
  },
  resetText: {color: colors.textSecondary, fontSize: 13},
  adminActiveBtn: {backgroundColor: colors.heart},
  adminActiveText: {color: colors.text, fontWeight: '600'},
  tokenRow: {
    flexDirection: 'row',
    marginHorizontal: 16,
    marginTop: 8,
    gap: 8,
  },
  tokenInput: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 8,
    color: colors.text,
    fontSize: 13,
  },
  tokenSubmitBtn: {
    backgroundColor: colors.primary,
    borderRadius: 10,
    paddingHorizontal: 16,
    justifyContent: 'center',
  },
  tokenSubmitText: {color: colors.text, fontSize: 13, fontWeight: '600'},
  empty: {alignItems: 'center', marginTop: 80},
  emptyIcon: {fontSize: 48, color: colors.heartInactive},
  emptyText: {color: colors.textSecondary, fontSize: 16, marginTop: 16},
  emptyHint: {color: colors.textMuted, fontSize: 13, marginTop: 8},
});
