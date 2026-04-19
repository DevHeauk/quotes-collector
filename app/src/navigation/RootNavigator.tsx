import React from 'react';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {colors} from '../constants/colors';
import Icon from 'react-native-vector-icons/Ionicons';

import {HomeScreen} from '../screens/HomeScreen';
import {ExploreScreen} from '../screens/ExploreScreen';
import {QuoteListScreen} from '../screens/QuoteListScreen';
import {QuoteDetailScreen} from '../screens/QuoteDetailScreen';
import {FavoritesScreen} from '../screens/FavoritesScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const stackScreenOptions = {
  headerStyle: {backgroundColor: colors.background},
  headerTintColor: colors.text,
  headerTitleStyle: {fontSize: 16},
};

function HomeStack() {
  return (
    <Stack.Navigator screenOptions={stackScreenOptions}>
      <Stack.Screen name="HomeMain" component={HomeScreen} options={{headerShown: false}} />
      <Stack.Screen name="QuoteDetail" component={QuoteDetailScreen} options={{title: '명언 상세'}} />
    </Stack.Navigator>
  );
}

function ExploreStack() {
  return (
    <Stack.Navigator screenOptions={stackScreenOptions}>
      <Stack.Screen name="ExploreMain" component={ExploreScreen} options={{title: '탐색'}} />
      <Stack.Screen name="QuoteList" component={QuoteListScreen} />
      <Stack.Screen name="QuoteDetail" component={QuoteDetailScreen} options={{title: '명언 상세'}} />
    </Stack.Navigator>
  );
}

function FavoritesStack() {
  return (
    <Stack.Navigator screenOptions={stackScreenOptions}>
      <Stack.Screen name="FavoritesMain" component={FavoritesScreen} options={{title: '좋아요'}} />
      <Stack.Screen name="QuoteDetail" component={QuoteDetailScreen} options={{title: '명언 상세'}} />
    </Stack.Navigator>
  );
}

function TabIcon({label, focused}: {label: string; focused: boolean}) {
  const iconMap: Record<string, [string, string]> = {
    '홈': ['home', 'home-outline'],
    '탐색': ['compass', 'compass-outline'],
    '좋아요': ['heart', 'heart-outline'],
  };
  const [filled, outline] = iconMap[label] || ['ellipse', 'ellipse-outline'];
  return (
    <Icon name={focused ? filled : outline} size={22} color={focused ? colors.primary : colors.textMuted} />
  );
}

export function RootNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        headerShown: false,
        tabBarStyle: {backgroundColor: colors.background, borderTopColor: colors.border},
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarIcon: ({focused}) => <TabIcon label={route.name} focused={focused} />,
      })}>
      <Tab.Screen name="홈" component={HomeStack} />
      <Tab.Screen name="탐색" component={ExploreStack} />
      <Tab.Screen name="좋아요" component={FavoritesStack} />
    </Tab.Navigator>
  );
}
