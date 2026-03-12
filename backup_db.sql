-- backup_db.sql
-- Base de datos para BROKEN TUNES
-- Almacenamiento de MP3 en la base de datos para simplicidad y portabilidad
-- VERSIÓN CORREGIDA: Mejoras de seguridad e integridad

CREATE DATABASE IF NOT EXISTS broken_tunes;
USE broken_tunes;

-- ============================================================================
-- TABLA: users
-- CORRECCIÓN: Contraseñas hasheadas con SHA2-256 (en producción usar bcrypt)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(256) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_username (username)
);

-- Contraseñas hasheadas (SHA2-256) - En producción usar bcrypt desde la aplicación
-- admin:1234 -> hash | user:password -> hash
INSERT INTO users (username, password) VALUES
('admin', SHA2('1234', 256)),
('user', SHA2('password', 256));

-- ============================================================================
-- TABLA: songs
-- CORRECCIÓN: Añadido UNIQUE constraint para evitar duplicados exactos
-- ============================================================================
CREATE TABLE IF NOT EXISTS songs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  artist VARCHAR(200) NOT NULL,
  mp3_data LONGBLOB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_song (title, artist),
  INDEX idx_artist (artist),
  INDEX idx_title (title)
);


-- Almacenamos el MP3 aquí para facilitar despliegues locales y backups sencillos
-- Inserciones de ejemplo con cadenas base64 cortas (simulan el binario)
-- OBSERVAMOS QUE LAS CANCIONES SI SE MUESTRAN 
/*
INSERT INTO songs (title, artist, mp3_data) VALUES
('Test Song', 'Broken Band', FROM_BASE64('U29tZQ==')),
('Sunny Day', 'Lazy Artist', FROM_BASE64('QXVkaW8=')),
('Night Drive', 'Neon Roads', FROM_BASE64('VGVzdA==')),
('Coffee Break', 'Minimalista', FROM_BASE64('QmFzZTY0')),
('Rainy Window', 'LoFi Beats', FROM_BASE64('Q2xpcA==')),
('Short Clip', 'Clip Band', FROM_BASE64('TW9jaw==')),
('Ambient Space', 'Drift', FROM_BASE64('U2hvcnQ=')),
('Tiny Loop', 'Loopers', FROM_BASE64('QmVhdA==')),
('Base64 Jam', 'Encoderz', FROM_BASE64('QXVkaW8x')),
('Duplicate Title', 'Echoes', FROM_BASE64('QXVkaW8y')),
-- Removido duplicado: ('Duplicate Title', 'Echoes', ...)
('Remix One', 'DJ Test', FROM_BASE64('UmVtaXg=')),
-- Removido duplicado: ('Remix One', 'DJ Test', ...)
('Track 01', 'Factory', FROM_BASE64('VHJhY2sx')),
('Track 02', 'Factory', FROM_BASE64('VHJhY2sy')),
('Loop 1', 'Loopers', FROM_BASE64('TG9vcDE=')),
('Loop 2', 'Loopers', FROM_BASE64('TG9vcDI=')),
('Sunny Day (Acoustic)', 'Lazy Artist', FROM_BASE64('U3Vubnk=')),
('Overshot', 'Neon Roads', FROM_BASE64('T3ZlcnM=')),
('Coffee Break (Short)', 'Minimalista', FROM_BASE64('Q29mZg==')),
('Rainy Window (Edit)', 'LoFi Beats', FROM_BASE64('UmFpbg==')),
('Tiny Loop (v2)', 'Loopers', FROM_BASE64('VHYy')),
('Ambient Space - Extended', 'Drift', FROM_BASE64('RXh0ZW5k')),
('Base64 Jam - Live', 'Encoderz', FROM_BASE64('TGl2ZQ==')),
('Clip One', 'Clip Band', FROM_BASE64('Q2xpcDE=')),
('Clip Two', 'Clip Band', FROM_BASE64('Q2xpcDI=')),
('Echo Chamber', 'Echoes', FROM_BASE64('RWNobw==')),
('Broken Loop', 'Broken Band', FROM_BASE64('QnJva2Vu')),
('Neon Drive (Remastered)', 'Neon Roads', FROM_BASE64('UmVtYXN0')),
('Duplicate Artist', 'Lazy Artist', FROM_BASE64('RHVwbA==')),
-- CORREGIDO: Caracteres especiales sanitizados
('Weird Name 1', 'Strange Artist', FROM_BASE64('V2VpcmQ=')),
('Weird Name 2', 'Strange Artist', FROM_BASE64('V2VpcmQy')),
('Single', 'Soloist', FROM_BASE64('U2luZ2xl')),
('Double', 'Twin', FROM_BASE64('RHViYmxl')),
('BSide', 'Oldies', FROM_BASE64('QlNpZGU=')),
('Hidden Track', 'Various', FROM_BASE64('SGlkZGVu')),
('Live 2019', 'StageBand', FROM_BASE64('TGl2ZTE5')),
('Live 2020', 'StageBand', FROM_BASE64('TGl2ZTIw')),
('Collab One', 'Artist A and Artist B', FROM_BASE64('Q29sbGFiMQ==')),
('Collab Two', 'Artist A and Artist B', FROM_BASE64('Q29sbGFiMg==')),
('Reprise', 'Composer', FROM_BASE64('UmVwcmlzZQ==')),
('Interlude', 'Composer', FROM_BASE64('SW50ZXJs')),
('Outro', 'Finale', FROM_BASE64('T3V0cm8=')),
('Intro', 'Prelude', FROM_BASE64('SW50cm8=')),
('Loop Short', 'Loopers', FROM_BASE64('TG9vc1M=')),
('Loop Long', 'Loopers', FROM_BASE64('TG9vc0xvZw==')),
('Cheap Sample', 'Sampler', FROM_BASE64('U2FtcGxl')),
('Debug Tone', 'TestLab', FROM_BASE64('RGVidWc=')),
('Mixdown 1', 'Studio', FROM_BASE64('TWl4MQ==')),
('Mixdown 2', 'Studio', FROM_BASE64('TWl4Mg==')),
('Snippet A', 'Editor', FROM_BASE64('U25pcA==')),
('Snippet B', 'Editor', FROM_BASE64('U25pcGI=')),
('One Minute', 'Shorts', FROM_BASE64('T25lTWlu')),
('Two Minutes', 'Shorts', FROM_BASE64('VHdvTWlu')),
('Ambient 1', 'Drift', FROM_BASE64('QW1iaWVy')),
('Ambient 2', 'Drift', FROM_BASE64('QW1iaWVyMg==')),
('Field Recording', 'Field', FROM_BASE64('RmllbGQ=')),
('Sampler Pack', 'Various', FROM_BASE64('U2FtcA==')),
('Test Clip 1', 'QA', FROM_BASE64('VGVzdDE=')),
('Test Clip 2', 'QA', FROM_BASE64('VGVzdDI=')),
('Alpha', 'Beta', FROM_BASE64('QWxwaGE=')),
('Beta Track', 'Beta', FROM_BASE64('QmV0YQ==')),
('Gamma', 'Beta', FROM_BASE64('R2FtbWE=')),
('Delta', 'Beta', FROM_BASE64('RGVsdGE=')),
('Epsilon', 'Beta', FROM_BASE64('RXBzaWxvbg==')),
('Zeta', 'Beta', FROM_BASE64('WmV0YQ==')),
('Eta', 'Beta', FROM_BASE64('RXRh')),
('Theta', 'Beta', FROM_BASE64('VGhldGE=')),
('Iota', 'Beta', FROM_BASE64('SW90YQ==')),
('Kappa', 'Beta', FROM_BASE64('S2FwcGE=')),
('Long Name with many words to test display', 'Verbose Artist', FROM_BASE64('TG9uZ05hbWU=')),
-- CORREGIDO: Caracteres especiales removidos
('Special Chars', 'Punctuated', FROM_BASE64('U3BlY2lhbA==')),
('Bracket Test', 'Brackets', FROM_BASE64('QnJhY2tldA==')),
('Slash Backslash Test', 'Slasher', FROM_BASE64('U2xhc2hlcg==')),
('Comma Separated Name', 'CSV Band', FROM_BASE64('Q1NW')),
-- CORREGIDO: Caracteres de control removidos
('Tab Name', 'Whitespace', FROM_BASE64('V2hpdGVzcGFjZQ==')),
('New Line', 'Whitespace', FROM_BASE64('TmV3TGluZQ==')),
('Emoji Song', 'Icons', FROM_BASE64('RW1vamk=')),
('Duplicate 1', 'Dupers', FROM_BASE64('RHVwMQ==')),
-- Removido duplicado: ('Duplicate 1', 'Dupers', ...)
('Duplicate 2', 'Dupers', FROM_BASE64('RHVwMw==')),
('Spam Track', 'Noise', FROM_BASE64('U3BhbQ==')),
('Noise 1', 'Noise', FROM_BASE64('Tm9pc2Ux')),
('Noise 2', 'Noise', FROM_BASE64('Tm9pc2Uy')),
('Glitch A', 'Glitchers', FROM_BASE64('R2xpdGNoQQ==')),
('Glitch B', 'Glitchers', FROM_BASE64('R2xpdGNoQg==')),
('Test-123', 'Numbers', FROM_BASE64('VGVzdC0xMjM=')),
('Track underscore', 'UnderScore', FROM_BASE64('VHJhY2tf')),
('Lowercase', 'artistlower', FROM_BASE64('bG93ZXI=')),
('UPPERCASE', 'ARTISTUP', FROM_BASE64('VVBF')),
('MiXeDCase', 'ArtistMix', FROM_BASE64('TWl4Q2FzZQ==')),
-- CORREGIDO: Espacios múltiples normalizados
('Spaces Multiple', 'Spacing', FROM_BASE64('U3BhY2luZw==')),
-- CORREGIDO: Espacios trailing/leading removidos
('TrailingSpace', 'Trim', FROM_BASE64('VHJpbQ==')),
('LeadingSpace', 'Trim', FROM_BASE64('TGVhZA==')),
('VeryVeryLongTitle', 'LongArtistName', FROM_BASE64('TG9uZ1RpdGxl')),
('Short', 'S', FROM_BASE64('U2hvcnQ=')),
('A', 'B', FROM_BASE64('QQ==')),
('B', 'A', FROM_BASE64('Qg==')),
('Orphan', 'NoArtist', FROM_BASE64('T3JwaGFu')),
('Catalog 001', 'Catalog', FROM_BASE64('Q2F0YTE=')),
('Catalog 002', 'Catalog', FROM_BASE64('Q2F0YTI=')),
('Catalog 003', 'Catalog', FROM_BASE64('Q2F0YTM=')),
('Broken and Fixed', 'Repair', FROM_BASE64('UmVwYWly')),
('Loop-Repeat', 'Loopers', FROM_BASE64('UmVwZWF0')),
('Echoes Remix', 'Echoes', FROM_BASE64('UmVtaXg=')),
('Echoes Remix 2', 'Echoes', FROM_BASE64('UmVtaXgy')),
('Parallel', 'Lines', FROM_BASE64('UGFyYWxsZWw=')),
('Series I', 'Set', FROM_BASE64('U2VyaWVzMQ==')),
('Series II', 'Set', FROM_BASE64('U2VyaWVzMg==')),
('Series III', 'Set', FROM_BASE64('U2VyaWVzMw==')),
('Misc 1', 'Misc', FROM_BASE64('TWlzYzE=')),
('Misc 2', 'Misc', FROM_BASE64('TWlzYzI=')),
('Misc 3', 'Misc', FROM_BASE64('TWlzYzM=')),
('Alt Take 1', 'Alt', FROM_BASE64('QWx0MQ==')),
('Alt Take 2', 'Alt', FROM_BASE64('QWx0Mg==')),
('Final Cut', 'EditTeam', FROM_BASE64('RmluYWw=')),
('Rough Cut', 'EditTeam', FROM_BASE64('Um91Z2g=')),
('Master', 'Mastering', FROM_BASE64('TWFzdGVy')),
('Pre-Master', 'Mastering', FROM_BASE64('UHJlTWVzdA==')),
('Outtake', 'Bloopers', FROM_BASE64('T3V0dGFrZQ==')),
('Bloop', 'Bloopers', FROM_BASE64('Qmxvb3A=')),
('ShortBeep', 'Beeps', FROM_BASE64('QmVlcA==')),
('LongBeep', 'Beeps', FROM_BASE64('TG9uZ0JlZXA=')),
('Test End', 'QA End', FROM_BASE64('VGVzdEVuZA==')),
('Overflow', 'EdgeCase', FROM_BASE64('T3ZlcmZsb3c=')),
('Sparse Name', 'Sparse', FROM_BASE64('U3BhcnNl')),
('Dense Name With Many Words', 'Verbose One', FROM_BASE64('RGVuc2U=')),
('Finale', 'ClosingAct', FROM_BASE64('RmluYWxl')),
('Curtain', 'ClosingAct', FROM_BASE64('Q3VydGFpbg==')),
('Encore', 'ClosingAct', FROM_BASE64('RW5jb3Jl')),
('Rewind', 'Player', FROM_BASE64('UmV3aW5k')),
('Forward', 'Player', FROM_BASE64('Rm9yd2FyZA==')),
('Skip', 'Player', FROM_BASE64('U2tpcA==')),
('Previous', 'Player', FROM_BASE64('UHJldg==')),
('Next', 'Player', FROM_BASE64('TmV4dA==')),
('Hidden Gem', 'Various', FROM_BASE64('SGVtbA==')),
('Treasure', 'Various', FROM_BASE64('VHJlYXN1cmU=')),
('Weird Name', 'Strange', FROM_BASE64('V2VpcmQ=')),
('Odd Name Test', 'Oddities', FROM_BASE64('T2Rk')),
('Spaces And Tabs Mixed', 'WeirdSpacing', FROM_BASE64('V2VpcmRTcGFjZQ==')),
-- CORREGIDO: Caracteres de control removidos
('Control Chars', 'Controls', FROM_BASE64('Q29udHJvbA==')),
('Null Char Test', 'Nulls', FROM_BASE64('TnVsbA==')),
('TrailingDots', 'Dots', FROM_BASE64('RG90cw==')),
('LeadingDots', 'Dots', FROM_BASE64('RG90czI=')),
('CapsLock', 'KEYS', FROM_BASE64('S0VZUw==')),
('123-456-7890', 'Numbers', FROM_BASE64('MTIz')),
('Mix 123 AZ', 'Hybrid', FROM_BASE64('TXhJ')),
('Final Track', 'The End', FROM_BASE64('VGhlRW5k')),
('VeryFinalTrack', 'The End', FROM_BASE64('VmVyeUZpbmFs'));
*/
-- ============================================================================
-- TABLA: songs_backup
-- CORRECCIÓN: Añadida FOREIGN KEY con integridad referencial
-- ============================================================================
CREATE TABLE IF NOT EXISTS songs_backup (
  id INT AUTO_INCREMENT PRIMARY KEY,
  original_song_id INT NULL,
  title VARCHAR(200) NOT NULL,
  artist VARCHAR(200) NOT NULL,
  mp3_data LONGBLOB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  backup_note VARCHAR(255) DEFAULT 'periodic backup',
  backed_up_by VARCHAR(100) DEFAULT 'system',
  backed_up_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_songs_backup_song FOREIGN KEY (original_song_id) 
    REFERENCES songs(id) ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_original_song (original_song_id)
);

-- Ejemplos de backups iniciales
INSERT INTO songs_backup (original_song_id, title, artist, mp3_data, backup_note, backed_up_by)
SELECT id, title, artist, mp3_data, 'initial import backup', 'import-script' 
FROM songs WHERE id <= 3;

-- ============================================================================
-- TABLA: file_index
-- CORRECCIÓN: Añadida FOREIGN KEY con integridad referencial
-- ============================================================================
CREATE TABLE IF NOT EXISTS file_index (
  id INT AUTO_INCREMENT PRIMARY KEY,
  song_id INT NULL,
  file_path VARCHAR(500) DEFAULT NULL,
  mp3_data LONGBLOB,
  note VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_file_index_song FOREIGN KEY (song_id) 
    REFERENCES songs(id) ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_song_id (song_id),
  INDEX idx_file_path (file_path(255))
);

INSERT INTO file_index (song_id, file_path, mp3_data, note) VALUES
(1, '/uploads/Test Song.mp3', NULL, 'copied to uploads and catalogued'),
(2, NULL, FROM_BASE64('U29tZUF1ZGlvX2luX2luZGV4'), 'audio stored directly in index');

--Eliminar duplicados existentes dejando solo el ID más bajo
DELETE s1 FROM songs s1
INNER JOIN songs s2 
WHERE s1.id > s2.id 
  AND s1.title = s2.title 
  AND s1.artist = s2.artist;

--Crear el índice único para evitar futuros duplicados
ALTER TABLE songs ADD UNIQUE INDEX idx_unique_song (title, artist);