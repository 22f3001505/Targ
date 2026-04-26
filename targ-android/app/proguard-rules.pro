# Project-specific release rules.
# Keep Retrofit/Gson model metadata available if release minification is enabled later.
-keepattributes Signature
-keepattributes RuntimeVisibleAnnotations
-keep class com.targ.app.data.model.** { *; }
-dontwarn javax.annotation.**
