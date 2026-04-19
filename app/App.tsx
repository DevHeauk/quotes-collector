import React, {useCallback, useEffect, useState} from 'react';
import {StatusBar} from 'react-native';
import {NavigationContainer} from '@react-navigation/native';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {RootNavigator} from './src/navigation/RootNavigator';
import {NeedPickerScreen} from './src/screens/onboarding/NeedPickerScreen';
import {QuoteTasteScreen} from './src/screens/onboarding/QuoteTasteScreen';
import {SplashScreen} from './src/screens/SplashScreen';
import {isOnboardingCompleted} from './src/storage/preferences';
import type {OnboardingStackParamList} from './src/types/navigation';

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

function App() {
  const [ready, setReady] = useState(false);
  const [splashDone, setSplashDone] = useState(false);
  const [onboarded, setOnboarded] = useState(false);

  useEffect(() => {
    isOnboardingCompleted().then(done => {
      setOnboarded(done);
      setReady(true);
    });
  }, []);

  const handleSplashFinish = useCallback(() => {
    setSplashDone(true);
  }, []);

  if (!ready || !splashDone) {
    return (
      <>
        <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
        <SplashScreen onFinish={handleSplashFinish} />
      </>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
      <NavigationContainer>
        <Stack.Navigator
          screenOptions={{headerShown: false}}
          initialRouteName={onboarded ? 'Main' : 'NeedPicker'}>
          <Stack.Screen name="NeedPicker" component={NeedPickerScreen} />
          <Stack.Screen name="QuoteTaste" component={QuoteTasteScreen} />
          <Stack.Screen name="Main" component={RootNavigator} />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default App;
