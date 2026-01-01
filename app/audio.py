def build_audio_block(audio_url: str, narrator_html: str, music_vol: float, version: int) -> str:
    """Return hidden audio elements and JS to handle playback/ducking."""
    return f"""
    <div style="display:none;">
        {"<audio autoplay loop id='bg-audio-"+str(version)+"' data-audio-player='bg'><source src='"+audio_url+"' type='audio/mp3'></audio>" if audio_url else ""}
        {narrator_html}
    </div>

    <script>
        (function() {{
            var bg = document.getElementById("bg-audio-{version}");
            var narr = document.getElementById("narrator");
            var userMusicVol = {music_vol};

            document.querySelectorAll('audio[data-audio-player="bg"]').forEach(function(a) {{
                if (a.id !== "bg-audio-{version}") {{ a.pause(); a.remove(); }}
            }});

            if (window.narratorFade) {{ clearInterval(window.narratorFade); window.narratorFade = null; }}

            if(bg) {{
                bg.volume = userMusicVol;
                bg.play().catch(e => console.log("BG Play Error:", e));
            }}

            if(narr) {{
                narr.volume = 1.0;
                var p = narr.play();
                if(p) p.catch(e => console.log("Narrator Play Error:", e));

                if(bg) {{
                    narr.onplay = function() {{
                        bg.volume = Math.max(0, userMusicVol * 0.25);
                    }};
                    narr.onended = function() {{
                        window.narratorFade = setInterval(function(){{
                            if(bg.volume < userMusicVol) {{
                                bg.volume = Math.min(userMusicVol, bg.volume + 0.05);
                            }} else {{
                                clearInterval(window.narratorFade);
                            }}
                        }}, 100);
                    }};
                }}
            }}
        }})();
    </script>
    """

