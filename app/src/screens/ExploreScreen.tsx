import React, {useEffect, useState} from 'react';
import {View, Text, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator} from 'react-native';
import {colors} from '../constants/colors';
import {fetchCategories, fetchSituations, fetchAuthors} from '../api/client';
import type {CategoryGroup, SituationGroup, AuthorListItem} from '../types';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';

type Tab = 'category' | 'situation' | 'author';

export function ExploreScreen({navigation}: {navigation: NativeStackNavigationProp<any>}) {
  const [tab, setTab] = useState<Tab>('category');
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

  return (
    <View style={styles.container}>
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
});
