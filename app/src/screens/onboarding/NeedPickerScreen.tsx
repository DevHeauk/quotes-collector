import React, {useState} from 'react';
import {View, Text, TouchableOpacity, StyleSheet} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import {colors} from '../../constants/colors';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {OnboardingStackParamList} from '../../types/navigation';

const NEEDS = [
  {key: 'motivation', emoji: '🔥', label: '힘을 내고 싶어요', desc: '의지가 약해질 때 불을 지펴주는 말'},
  {key: 'comfort', emoji: '🌊', label: '위로가 필요해요', desc: '힘든 시기를 견딜 수 있게 해주는 말'},
  {key: 'reflection', emoji: '🪞', label: '나를 돌아보고 싶어요', desc: '삶의 의미를 생각하게 해주는 말'},
  {key: 'insight', emoji: '💡', label: '시야를 넓히고 싶어요', desc: '새로운 관점을 열어주는 말'},
  {key: 'relationship', emoji: '💛', label: '사람 사이에서', desc: '관계에 대해 생각하게 해주는 말'},
  {key: 'humor', emoji: '😄', label: '웃고 싶어요', desc: '위트 있는 한마디'},
];

type Props = NativeStackScreenProps<OnboardingStackParamList, 'NeedPicker'>;

export function NeedPickerScreen({navigation}: Props) {
  const [selected, setSelected] = useState<string[]>([]);

  const toggle = (key: string) => {
    setSelected(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : prev.length < 3 ? [...prev, key] : prev,
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.step}>1 / 2</Text>
        <Text style={styles.title}>매일 어떤 말이{'\n'}필요하세요?</Text>
        <Text style={styles.subtitle}>마음에 드는 것을 골라주세요 (최대 3개)</Text>
      </View>

      <View style={styles.list}>
        {NEEDS.map(n => {
          const active = selected.includes(n.key);
          return (
            <TouchableOpacity
              key={n.key}
              style={[styles.card, active && styles.cardActive]}
              onPress={() => toggle(n.key)}
              activeOpacity={0.7}>
              <Text style={styles.emoji}>{n.emoji}</Text>
              <View style={styles.cardText}>
                <Text style={[styles.cardLabel, active && styles.cardLabelActive]}>{n.label}</Text>
                <Text style={styles.cardDesc}>{n.desc}</Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </View>

      <TouchableOpacity
        style={[styles.nextBtn, selected.length === 0 && styles.nextBtnDisabled]}
        disabled={selected.length === 0}
        onPress={() => navigation.navigate('QuoteTaste', {needs: selected})}>
        <Text style={styles.nextText}>다음</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background, padding: 24},
  header: {marginTop: 20, marginBottom: 28},
  step: {color: colors.primary, fontSize: 14, fontWeight: '600', marginBottom: 8},
  title: {color: colors.text, fontSize: 24, fontWeight: '700', marginBottom: 8},
  subtitle: {color: colors.textMuted, fontSize: 14},
  list: {gap: 10},
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 18,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  cardActive: {borderColor: colors.primary, backgroundColor: '#1e3a5f'},
  emoji: {fontSize: 28, marginRight: 16},
  cardText: {flex: 1},
  cardLabel: {color: colors.text, fontSize: 16, fontWeight: '600', marginBottom: 2},
  cardLabelActive: {color: colors.primary},
  cardDesc: {color: colors.textMuted, fontSize: 12, lineHeight: 18},
  nextBtn: {
    position: 'absolute',
    bottom: 40,
    left: 24,
    right: 24,
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
  },
  nextBtnDisabled: {backgroundColor: colors.surfaceLight, opacity: 0.5},
  nextText: {color: colors.background, fontSize: 16, fontWeight: '700'},
});
