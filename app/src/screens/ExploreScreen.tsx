import React, {useEffect, useRef, useState} from 'react';
import {View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator, Alert} from 'react-native';
import {colors} from '../constants/colors';
import {fetchCategories, fetchSituations, fetchAuthors} from '../api/client';
import {getAdminToken, setAdminToken, clearAdminToken} from '../storage/admin';
import type {CategoryGroup, SituationGroup, AuthorListItem} from '../types';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';

type Tab = 'category' | 'situation' | 'author';

export function ExploreScreen({navigation}: {navigation: NativeStackNavigationProp<any>}) {
  const [tab, setTab] = useState<Tab>('category');
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [tokenInput, setTokenInput] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const tapCount = useRef(0);
  const tapTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    getAdminToken().then(t => setIsAdmin(!!t));
  }, []);

  useEffect(() => {
    navigation.setOptions({
      headerTitle: () => (
        <TouchableOpacity onPress={handleTitleTap} activeOpacity={1}>
          <Text style={{color: colors.text, fontSize: 16, fontWeight: '600'}}>탐색</Text>
        </TouchableOpacity>
      ),
    });
  }, [navigation]);
  const [categories, setCategories] = useState<CategoryGroup[]>([]);
  const [situations, setSituations] = useState<SituationGroup[]>([]);
  const [authors, setAuthors] = useState<AuthorListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    if (tab === 'category') {
      fetchCategories().then(setCategories).finally(() => setLoading(false));
    } else if (tab === 'situation') {
      fetchSituations().then(setSituations).finally(() => setLoading(false));
    } else {
      fetchAuthors(1, 50).then(setAuthors).finally(() => setLoading(false));
    }
  }, [tab]);

  const handleTitleTap = () => {
    tapCount.current += 1;
    if (tapTimer.current) clearTimeout(tapTimer.current);
    tapTimer.current = setTimeout(() => { tapCount.current = 0; }, 3000);
    if (tapCount.current >= 10) {
      tapCount.current = 0;
      if (isAdmin) return; // 이미 관리자면 무시
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

  const handleAdminOff = () => {
    Alert.alert('관리자 모드 해제', '관리자 모드를 해제하시겠습니까?', [
      {text: '취소', style: 'cancel'},
      {text: '해제', onPress: async () => {
        await clearAdminToken();
        setIsAdmin(false);
      }},
    ]);
  };

  return (
    <View style={styles.container}>
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
      {isAdmin && (
        <TouchableOpacity style={styles.adminOffBtn} onPress={handleAdminOff}>
          <Text style={styles.adminOffText}>관리자 모드 해제</Text>
        </TouchableOpacity>
      )}
      <View style={styles.tabs}>
        {(['category', 'situation', 'author'] as Tab[]).map(t => (
          <TouchableOpacity
            key={t}
            style={[styles.tab, tab === t && styles.tabActive]}
            onPress={() => setTab(t)}>
            <Text style={[styles.tabText, tab === t && styles.tabTextActive]}>
              {t === 'category' ? '카테고리' : t === 'situation' ? '상황' : '저자'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <ActivityIndicator size="large" color={colors.primary} style={{marginTop: 40}} />
      ) : tab === 'category' ? (
        <FlatList
          data={categories}
          keyExtractor={item => item.group_name}
          renderItem={({item}) => (
            <TouchableOpacity
              style={styles.item}
              onPress={() => navigation.navigate('QuoteList', {
                title: item.group_name,
                filter: {keyword_group: item.group_name},
              })}>
              <Text style={styles.itemTitle}>{item.group_name}</Text>
              <Text style={styles.itemCount}>{item.count}개</Text>
            </TouchableOpacity>
          )}
        />
      ) : tab === 'situation' ? (
        <FlatList
          data={situations}
          keyExtractor={item => item.group_name}
          renderItem={({item}) => (
            <TouchableOpacity
              style={styles.item}
              onPress={() => navigation.navigate('QuoteList', {
                title: item.group_name,
                filter: {situation_group: item.group_name},
              })}>
              <Text style={styles.itemTitle}>{item.group_name}</Text>
              <Text style={styles.itemCount}>{item.count}개</Text>
            </TouchableOpacity>
          )}
        />
      ) : (
        <FlatList
          data={authors}
          keyExtractor={item => item.id}
          renderItem={({item}) => (
            <TouchableOpacity
              style={styles.item}
              onPress={() => navigation.navigate('QuoteList', {
                title: item.name,
                filter: {author_id: item.id},
              })}>
              <View>
                <Text style={styles.itemTitle}>{item.name}</Text>
                <Text style={styles.itemSub}>{item.profession} · {item.nationality}</Text>
              </View>
              <Text style={styles.itemCount}>{item.quote_count}개</Text>
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background},
  tabs: {flexDirection: 'row', paddingHorizontal: 16, paddingTop: 12, gap: 8},
  tab: {flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 10, backgroundColor: colors.surface},
  tabActive: {backgroundColor: colors.primary},
  tabText: {color: colors.textSecondary, fontSize: 14, fontWeight: '500'},
  tabTextActive: {color: colors.background, fontWeight: '700'},
  item: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  itemTitle: {color: colors.text, fontSize: 16},
  itemSub: {color: colors.textMuted, fontSize: 12, marginTop: 2},
  itemCount: {color: colors.textMuted, fontSize: 14},
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
  adminOffBtn: {
    alignSelf: 'center',
    marginTop: 8,
    paddingHorizontal: 14,
    paddingVertical: 6,
    backgroundColor: colors.heart,
    borderRadius: 8,
  },
  adminOffText: {color: colors.text, fontSize: 12, fontWeight: '600'},
});
