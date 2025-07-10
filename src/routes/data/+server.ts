// src/routes/+page.server.ts
import { supabase } from '../../lib/supabaseClient';
import { json } from '@sveltejs/kit';

export async function POST({ request }) {
  const newRows = await request.json();

  const { data, error } = await supabase
    .from('chupps_23_25_full_duplicate_2')
    .insert(newRows);

  if (error) {
    console.error('Insert Error:', error);
    return json({ success: false, error });
  }

  return json({ success: true, data });
}