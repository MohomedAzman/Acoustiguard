import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime

from .database import get_connection
from .models import ScanResult, AcousticFeatures, RiskAssessment, Recommendation, Settings


class ScanRepository:
    """Repository for scan-related database operations."""
    
    @staticmethod
    def save_scan(scan_result):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO scans 
                (scan_date, scan_time, duration_seconds, risk_score, risk_level, masking_enabled)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                scan_result.scan_date, scan_result.scan_time, scan_result.duration_seconds,
                scan_result.risk_score, scan_result.risk_level,
                1 if scan_result.masking_enabled else 0,
            ))
            scan_id = cursor.lastrowid
            
            if scan_result.acoustic_features:
                f = scan_result.acoustic_features
                cursor.execute("""
                    INSERT INTO acoustic_features
                    (scan_id, rms_energy, spectral_centroid, spectral_bandwidth, 
                     spectral_rolloff, zero_crossing_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (scan_id, f.rms_energy, f.spectral_centroid, f.spectral_bandwidth,
                      f.spectral_rolloff, f.zero_crossing_rate))
            
            for rec in scan_result.recommendations:
                cursor.execute("""
                    INSERT INTO recommendations (scan_id, recommendation_text, priority)
                    VALUES (?, ?, ?)
                """, (scan_id, rec.recommendation_text, rec.priority))
            
            conn.commit()
            return scan_id
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to save scan: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def get_scan_by_id(scan_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            cursor.execute("SELECT * FROM acoustic_features WHERE scan_id = ?", (scan_id,))
            f_row = cursor.fetchone()
            features = None
            if f_row:
                features = AcousticFeatures(
                    rms_energy=f_row['rms_energy'] or 0.0,
                    spectral_centroid=f_row['spectral_centroid'] or 0.0,
                    spectral_bandwidth=f_row['spectral_bandwidth'] or 0.0,
                    spectral_rolloff=f_row['spectral_rolloff'] or 0.0,
                    zero_crossing_rate=f_row['zero_crossing_rate'] or 0.0,
                )
            
            cursor.execute("SELECT * FROM recommendations WHERE scan_id = ? ORDER BY priority DESC", (scan_id,))
            recs = [Recommendation(r['recommendation_text'], r['priority']) for r in cursor.fetchall()]
            
            return ScanResult(
                scan_id=row['id'], scan_date=row['scan_date'], scan_time=row['scan_time'],
                duration_seconds=row['duration_seconds'],
                risk_assessment=RiskAssessment(row['risk_score'], row['risk_level']),
                acoustic_features=features, recommendations=recs,
                masking_enabled=bool(row['masking_enabled']),
            )
        finally:
            conn.close()
    
    @staticmethod
    def get_all_scans(limit=100):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, scan_date, scan_time, risk_score, risk_level,
                       duration_seconds, masking_enabled, created_at
                FROM scans ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            return [{
                'id': r['id'], 'date': r['scan_date'], 'time': r['scan_time'],
                'risk': r['risk_level'], 'risk_score': r['risk_score'],
                'duration': r['duration_seconds'], 'masking_enabled': bool(r['masking_enabled']),
            } for r in cursor.fetchall()]
        finally:
            conn.close()
    
    @staticmethod
    def clear_all_scans() -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM scans")
            count = cursor.rowcount
            conn.commit()
            return int(count) if count is not None else 0
        finally:
            conn.close()


class SettingsRepository:
    """Repository for settings operations."""
    
    @staticmethod
    def get_settings():
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT key, value FROM settings")
            data = {r['key']: r['value'] for r in cursor.fetchall()}
            return Settings.from_dict(data)
        finally:
            conn.close()
    
    @staticmethod
    def save_settings(settings):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            for key, value in settings.to_dict().items():
                v = 'true' if value is True else 'false' if value is False else str(value)
                cursor.execute("""
                    INSERT INTO settings (key, value) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
                """, (key, v))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to save settings: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def get_setting(key, default=""):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
        finally:
            conn.close()


def get_last_scan():
    scans = ScanRepository.get_all_scans(limit=1)
    return scans[0] if scans else None
