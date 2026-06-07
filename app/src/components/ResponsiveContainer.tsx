import React from 'react';
import {View, StyleSheet, ViewStyle, StyleProp} from 'react-native';
import {useResponsive} from '../hooks/useResponsive';
import {colors} from '../constants/colors';

interface Props {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  /** 콘텐츠 최대폭 덮어쓰기 (기본: 사이즈 클래스 기준) */
  maxWidth?: number;
}

/**
 * 콘텐츠를 화면 중앙에 두고 넓은 화면(태블릿/폴드 펼침)에서 최대폭으로 제한한다.
 * compact에서는 사실상 전체폭이라 폰 레이아웃은 그대로 유지된다.
 */
export function ResponsiveContainer({children, style, maxWidth}: Props) {
  const {contentMaxWidth} = useResponsive();
  return (
    <View style={styles.outer}>
      <View style={[styles.inner, {maxWidth: maxWidth ?? contentMaxWidth}, style]}>
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  outer: {
    flex: 1,
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  inner: {
    flex: 1,
    width: '100%',
    alignSelf: 'center',
  },
});
