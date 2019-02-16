angular.module('mySunBuddy.public.home', ['ui.bootstrap']);

angular.module('mySunBuddy.dashboard.common', ['ui.bootstrap']);

angular.module('mySunBuddy.public.signIn', ['ui.bootstrap']);

angular.module('mySunBuddy.public', ['mySunBuddy.public.signIn', 'mySunBuddy.public.home']);

angular.module('mySunBuddy.dashboard', ['mySunBuddy.dashboard.common', 'mySunBuddy.dashboard.seller']);

angular.module('mySunBuddy.common', ['ui.bootstrap']);

angular.module('mySunBuddy.controllers', ['ui.bootstrap', 'ngMap']);

angular.module('mySunBuddy.dashboard.seller', ['ui.bootstrap']);

angular.module('mySunBuddy.filter', []);

angular.module('mySunBuddy.services', []);