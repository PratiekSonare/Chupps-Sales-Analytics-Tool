// src/routes/+page.server.ts
import type { PageServerLoad } from './$types';
import { supabase } from '../lib/supabaseClient';

export const load: PageServerLoad = async () => {
  // Query the table
  const { data: wo_centro_prophet, error: err1 } = await supabase.from('wo_centro_prophet').select('*');
  if (err1) {
    console.error('Supabase error:', err1);
    return { wo_centro_prophet: [] }; // Return an empty array on error
  } else {
    console.log('Data fetched successfully!');
  }
  return {
    wo_centro_prophet
  };    
};
