# TRUSTLENS AI Release ProGuard / R8 Rules
-keep class ai.trustlens.mobile.** { *; }
-keep @com.getcapacitor.annotation.CapacitorPlugin class * { *; }
-keepclassmembers class * {
    @com.getcapacitor.PluginMethod <methods>;
}
-keep class androidx.security.crypto.** { *; }
-dontwarn com.google.crypto.tink.**
