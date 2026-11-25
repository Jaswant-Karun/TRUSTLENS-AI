package ai.trustlens.mobile;

import android.content.Context;
import android.content.SharedPreferences;

import androidx.security.crypto.EncryptedSharedPreferences;
import androidx.security.crypto.MasterKey;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "TrustLensSecureStorage")
public class TrustLensSecureStoragePlugin extends Plugin {
    private static final String PREFS_NAME = "trustlens_secure_prefs";

    private SharedPreferences getEncryptedPrefs() throws Exception {
        Context context = getContext().getApplicationContext();
        MasterKey masterKey = new MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build();

        return EncryptedSharedPreferences.create(
                context,
                PREFS_NAME,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        );
    }

    @PluginMethod
    public void setToken(PluginCall call) {
        String key = call.getString("key");
        String value = call.getString("value");
        if (key == null || value == null) {
            call.reject("Missing key or value");
            return;
        }
        try {
            getEncryptedPrefs().edit().putString(key, value).apply();
            call.resolve();
        } catch (Exception e) {
            call.reject("Failed to store token securely", e);
        }
    }

    @PluginMethod
    public void getToken(PluginCall call) {
        String key = call.getString("key");
        if (key == null) {
            call.reject("Missing key");
            return;
        }
        try {
            String val = getEncryptedPrefs().getString(key, null);
            JSObject ret = new JSObject();
            ret.put("value", val);
            call.resolve(ret);
        } catch (Exception e) {
            call.reject("Failed to read token securely", e);
        }
    }

    @PluginMethod
    public void clearToken(PluginCall call) {
        String key = call.getString("key");
        if (key == null) {
            call.reject("Missing key");
            return;
        }
        try {
            getEncryptedPrefs().edit().remove(key).apply();
            call.resolve();
        } catch (Exception e) {
            call.reject("Failed to clear token securely", e);
        }
    }
}
