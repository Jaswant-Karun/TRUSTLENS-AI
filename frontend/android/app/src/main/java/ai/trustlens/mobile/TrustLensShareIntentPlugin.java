package ai.trustlens.mobile;

import android.content.ContentResolver;
import android.content.Intent;
import android.net.Uri;
import android.util.Base64;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;

@CapacitorPlugin(name = "TrustLensShareIntent")
public class TrustLensShareIntentPlugin extends Plugin {
    private static final int MAX_SHARED_IMAGE_BYTES = 10 * 1024 * 1024;
    private JSObject pendingShare = null;

    @Override
    public void load() {
        Intent intent = getActivity() != null ? getActivity().getIntent() : null;
        if (intent != null) {
            processIncomingIntent(intent);
        }
    }

    @Override
    protected void handleOnNewIntent(Intent intent) {
        super.handleOnNewIntent(intent);
        processIncomingIntent(intent);
        if (pendingShare != null) {
            notifyListeners("shareReceived", pendingShare);
        }
    }

    @PluginMethod
    public void getPendingShare(PluginCall call) {
        JSObject result = pendingShare != null ? pendingShare : new JSObject();
        pendingShare = null;
        call.resolve(result);
    }

    private void processIncomingIntent(Intent intent) {
        if (intent == null || !Intent.ACTION_SEND.equals(intent.getAction())) {
            return;
        }
        String type = intent.getType();
        if (type == null) {
            return;
        }

        if ("text/plain".equals(type)) {
            String sharedText = intent.getStringExtra(Intent.EXTRA_TEXT);
            if (sharedText != null && !sharedText.trim().isEmpty()) {
                JSObject payload = new JSObject();
                payload.put("kind", "text");
                payload.put("text", sharedText.trim());
                pendingShare = payload;
            }
            return;
        }

        if (type.startsWith("image/")) {
            Uri imageUri = intent.getParcelableExtra(Intent.EXTRA_STREAM);
            if (imageUri == null) {
                return;
            }
            try {
                ContentResolver resolver = getContext().getContentResolver();
                String resolvedMime = resolver.getType(imageUri);
                if (resolvedMime == null) {
                    resolvedMime = type;
                }
                if (!resolvedMime.equals("image/jpeg")
                        && !resolvedMime.equals("image/png")
                        && !resolvedMime.equals("image/webp")) {
                    return;
                }

                byte[] bytes = readBoundedBytes(resolver, imageUri, MAX_SHARED_IMAGE_BYTES);
                if (bytes == null || bytes.length == 0 || !hasValidMagicHeader(bytes)) {
                    return;
                }

                JSObject payload = new JSObject();
                payload.put("kind", "image");
                payload.put("mimeType", resolvedMime);
                payload.put("base64", Base64.encodeToString(bytes, Base64.NO_WRAP));
                pendingShare = payload;
            } catch (Exception ignored) {
                // Reject malformed or oversized shared content silently.
            }
        }
    }

    private static byte[] readBoundedBytes(ContentResolver resolver, Uri uri, int maxBytes) throws Exception {
        try (InputStream is = resolver.openInputStream(uri);
             ByteArrayOutputStream buffer = new ByteArrayOutputStream()) {
            if (is == null) return null;
            byte[] chunk = new byte[8192];
            int total = 0;
            int read;
            while ((read = is.read(chunk)) != -1) {
                total += read;
                if (total > maxBytes) {
                    return null;
                }
                buffer.write(chunk, 0, read);
            }
            return buffer.toByteArray();
        }
    }

    private static boolean hasValidMagicHeader(byte[] b) {
        if (b.length < 4) return false;
        boolean isPng = (b[0] & 0xFF) == 0x89 && b[1] == 0x50 && b[2] == 0x4E && b[3] == 0x47;
        boolean isJpeg = (b[0] & 0xFF) == 0xFF && (b[1] & 0xFF) == 0xD8 && (b[2] & 0xFF) == 0xFF;
        boolean isWebp = b.length >= 12
                && b[0] == 0x52 && b[1] == 0x49 && b[2] == 0x46 && b[3] == 0x46
                && b[8] == 0x57 && b[9] == 0x45 && b[10] == 0x42 && b[11] == 0x50;
        return isPng || isJpeg || isWebp;
    }
}
