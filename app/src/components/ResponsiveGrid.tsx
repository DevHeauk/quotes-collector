import React from 'react';
import {FlatList, FlatListProps, View, ListRenderItem} from 'react-native';
import {useResponsive} from '../hooks/useResponsive';

interface Props<T> extends Omit<FlatListProps<T>, 'numColumns' | 'key'> {
  /** 열 사이 간격 (기본 12) */
  columnGap?: number;
  /** 그리드 최대폭 (기본: 제한 없음, 큰 화면 과확장 방지용 1200 권장) */
  gridMaxWidth?: number;
}

/**
 * 사이즈 클래스에 따라 열 수를 바꾸는 FlatList.
 * compact=1열, medium=2열, expanded=3열. 폴드 접기/펴기 시 자동 재배치된다.
 * 아이템은 셀(flex:1)로 감싸 균등 폭을 보장하므로, 카드에는 가로 마진을 두지 않는다.
 */
export function ResponsiveGrid<T>({
  renderItem,
  columnGap = 12,
  gridMaxWidth = 1200,
  contentContainerStyle,
  columnWrapperStyle,
  ...rest
}: Props<T>) {
  const {columns, gutter} = useResponsive();

  const gridRenderItem: ListRenderItem<T> | null | undefined = renderItem
    ? info => (
        <View style={columns > 1 ? {flex: 1, maxWidth: `${100 / columns}%`} : undefined}>
          {renderItem(info)}
        </View>
      )
    : renderItem;

  return (
    <FlatList
      {...rest}
      // numColumns 변경 시 FlatList는 재마운트가 필요하다.
      key={`cols-${columns}`}
      numColumns={columns}
      renderItem={gridRenderItem}
      columnWrapperStyle={
        columns > 1
          ? [{gap: columnGap, paddingHorizontal: gutter}, columnWrapperStyle]
          : undefined
      }
      contentContainerStyle={[
        {
          maxWidth: gridMaxWidth,
          width: '100%',
          alignSelf: 'center',
          paddingHorizontal: columns > 1 ? 0 : gutter,
        },
        contentContainerStyle,
      ]}
    />
  );
}
